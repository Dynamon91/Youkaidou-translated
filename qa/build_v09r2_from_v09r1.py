#!/usr/bin/env python3
"""Rebuild v0.9r2 journey-houses IPS using the verified v0.9r1 IPS as baseline.

Requires no commercial ROM. For gameplay, apply v0.8 then the generated v0.9r2
direct patch to a clean user-owned AFUJ ROM. Never stack v0.9r1 and v0.9r2.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from script_codec import decode_lzss, encode_lzss_literals, encode_story

REFERENCE_SHA256 = "e93985ac4b66c72f35ea1c48df312931b4c0677b1d8bf307400eb504ca086594"
EXPECTED_OFFSETS = {"journey_houses_line_013": 0x4CE, "journey_houses_line_023": 0x652}
SOURCE = ROOT / "Youkaidou_English_v09r1_journey_houses.ips"
TARGET = ROOT / "Youkaidou_English_v09r2_journey_houses.ips"

def parse_ips(data):
    if data[:5] != b"PATCH":
        raise ValueError("Not an IPS file")
    records = []
    p = 5
    while data[p:p+3] != b"EOF":
        if p+5 > len(data):
            raise ValueError("Truncated IPS")
        offset = int.from_bytes(data[p:p+3], "big")
        size = int.from_bytes(data[p+3:p+5], "big")
        p += 5
        if not size:
            raise ValueError("Unexpected RLE in reference patch")
        records.append((offset, p, size))
        p += size
    if p != len(data)-3:
        raise ValueError("Unexpected IPS tail")
    return records

def main():
    base = SOURCE.read_bytes()
    if hashlib.sha256(base).hexdigest() != REFERENCE_SHA256:
        raise ValueError("Reference IPS SHA-256 mismatch")
    records = parse_ips(base)
    if len(records) != 3 or [x[0] for x in records] != [0x15E8E0, 0x76E174, 0x7C4002]:
        raise ValueError("Unexpected ROM write ranges")
    offset, start, size = records[-1]
    if size != 2886:
        raise ValueError("Unexpected event data size")
    before_packed = b"\x00\x00" + base[start:start+size] + b"\x00"
    before, consumed = decode_lzss(before_packed)
    if len(before) != 2564 or consumed != 2889:
        raise ValueError("Reference event asset changed")
    data = bytearray(before)
    previous = json.loads((ROOT / "journey_houses_translations_v09r1.json").read_text(encoding="utf-8"))
    updated = json.loads((ROOT / "journey_houses_translations_v09r2.json").read_text(encoding="utf-8"))
    old_items = {x["id"]:x for x in previous["strings"]}
    new_items = {x["id"]:x for x in updated["strings"]}
    if old_items.keys() != new_items.keys() or len(old_items) != 26:
        raise ValueError("Translation record inventory changed")
    for id_, location in EXPECTED_OFFSETS.items():
        item0, item1 = old_items[id_], new_items[id_]
        old_bytes, old_cells, old_vars = encode_story(item0["english"])
        new_bytes, new_cells, new_vars = encode_story(item1["english"])
        if old_cells != new_cells or old_vars != new_vars or old_cells > item1["max_cells"]:
            raise ValueError("Cell or variable regression: " + id_)
        if data[location:location+len(old_bytes)] != old_bytes:
            raise ValueError("Baseline text changed: " + id_)
        if before.count(old_bytes) != 1:
            raise ValueError("Expected unique text: " + id_)
        data[location:location+len(new_bytes)] = new_bytes
    if sum(old_items[k]["english"] != new_items[k]["english"] for k in old_items) != 2:
        raise ValueError("Unexpected manifest modification")
    if data[:368] != before[:368] or len(data) != len(before):
        raise ValueError("Event header/table changed")
    def controls(raw):
        return [int.from_bytes(raw[i:i+2],"little") for i in range(368, len(raw), 2)
                if int.from_bytes(raw[i:i+2],"little") >= 0x4000]
    if controls(data) != controls(before):
        raise ValueError("Event VM opcodes changed")
    compressed = encode_lzss_literals(bytes(data))
    if len(compressed) != 2889 or compressed[:2] != b"\x00\x00" or compressed[-1:] != b"\x00":
        raise ValueError("Compressed layout changed")
    if decode_lzss(compressed)[0] != data:
        raise ValueError("LZSS round-trip failure")
    result = bytearray(base)
    result[start:start+size] = compressed[2:-1]
    if parse_ips(result) != records:
        raise ValueError("IPS record structure changed")
    if any(result[i] != base[i] for i in range(len(base)) if not start <= i < start+size):
        raise ValueError("Changed pointer/header bytes")
    TARGET.write_bytes(result)
    print(json.dumps({"result":"PASS — static verification only",
                      "file":str(TARGET), "bytes":len(result),
                      "sha256":hashlib.sha256(result).hexdigest(),
                      "changed_strings":list(EXPECTED_OFFSETS),
                      "emulator_test":"PENDING"},indent=2))

if __name__ == "__main__":
    main()
