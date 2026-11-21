#!/usr/bin/env python3
"""Audit v09r2 IPS stack without needing a Japanese ROM.

Proves text slot encoding, pointer footprint, VM control preservation, IPS
non-overlap against v08, and literal LZSS consistency. Not an emulator test.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from script_codec import decode_lzss, encode_lzss_literals, encode_story


def ips_records(blob):
    if not blob.startswith(b"PATCH"):
        raise ValueError("Invalid IPS header")
    entries = []
    i = 5
    while i < len(blob):
        if blob[i:i + 3] == b"EOF":
            if i + 3 != len(blob):
                raise ValueError("IPS truncation/resize tail unsupported")
            return entries
        if i + 5 > len(blob):
            raise ValueError("Truncated IPS record")
        off = int.from_bytes(blob[i:i + 3], 'big')
        n = int.from_bytes(blob[i + 3:i + 5], 'big')
        i += 5
        if n:
            if i + n > len(blob):
                raise ValueError("Truncated IPS payload")
            data = blob[i:i + n]
            i += n
        else:
            if i + 3 > len(blob):
                raise ValueError("Truncated IPS RLE")
            repeat = int.from_bytes(blob[i:i + 2], 'big')
            data = blob[i + 2:i + 3] * repeat
            i += 3
        if not data or off + len(data) > 0x1000000:
            raise ValueError("Invalid IPS write range")
        entries.append((off, data))
    raise ValueError("Missing IPS EOF")


def load_event(records):
    events = [payload for off, payload in records if off == 0x7C4002]
    if len(events) != 1 or len(events[0]) != 2886:
        raise ValueError("Missing relocated event data")
    packed = b'\x00\x00' + events[0] + b'\x00'
    raw, used = decode_lzss(packed)
    if len(raw) != 2564 or used != 2889:
        raise ValueError("Event LZSS boundary mismatch")
    if encode_lzss_literals(raw) != packed:
        raise ValueError("Event LZSS round-trip failure")
    return raw


def vm_controls(raw):
    return [int.from_bytes(raw[i:i + 2], 'little')
            for i in range(368, len(raw), 2)
            if int.from_bytes(raw[i:i + 2], 'little') >= 0x4000]


def audit(root=ROOT):
    read = lambda name: (root / name).read_bytes()
    base = ips_records(read('Youkaidou_English_v08.ips'))
    old_patch = read('Youkaidou_English_v09r1_journey_houses.ips')
    updated_patch = read('Youkaidou_English_v09r2_journey_houses.ips')
    expected_hash = 'e93985ac4b66c72f35ea1c48df312931b4c0677b1d8bf307400eb504ca086594'
    if hashlib.sha256(old_patch).hexdigest() != expected_hash:
        raise ValueError("Reference v09r1 SHA-256 mismatch")
    old_records = ips_records(old_patch)
    new_records = ips_records(updated_patch)
    ranges = [(0x15E8E0, 3), (0x76E174, 3), (0x7C4002, 2886)]
    for records in (old_records, new_records):
        if [(off, len(data)) for off, data in records] != ranges:
            raise ValueError("Unexpected addon write ranges")
        if any(a < d + len(payload) and d < a + len(data)
               for a, data in base for d, payload in records):
            raise ValueError("v08/addon IPS overlap")
    if old_records[:2] != new_records[:2]:
        raise ValueError("Event pointer writes changed")
    old = load_event(old_records)
    new = load_event(new_records)
    if old[:368] != new[:368] or vm_controls(old) != vm_controls(new):
        raise ValueError("Event table / VM control changed")
    prior = json.loads(read('journey_houses_translations_v09r1.json'))
    updated = json.loads(read('journey_houses_translations_v09r2.json'))
    old_by_id = {x['id']: x for x in prior['strings']}
    items = sorted(updated['strings'], key=lambda x: int(x['offset'], 16))
    if len(old_by_id) != 26 or len(items) != 26 or set(old_by_id) != {x['id'] for x in items}:
        raise ValueError("Translation inventory mismatch")
    delta = 0
    modified = []
    for item in items:
        previous = old_by_id[item['id']]
        old_text, old_cells, old_vars = encode_story(previous['english'])
        encoded, cells, variables = encode_story(item['english'])
        if len(encoded) % 2 or not 0 < cells <= item['max_cells']:
            raise ValueError("Textbox overflow: " + item['id'])
        if variables != old_vars:
            raise ValueError("Variable changed: " + item['id'])
        location = int(item['offset'], 16) + delta
        marker = int(item['marker'], 16).to_bytes(2, 'little')
        if new[location - 2:location] != marker or new[location:location + len(encoded)] != encoded:
            raise ValueError("Text/marker mismatch: " + item['id'])
        if previous['english'] != item['english']:
            if cells != old_cells or len(encoded) != len(old_text):
                raise ValueError("Modified text no longer has same width: " + item['id'])
            modified.append(item['id'])
        delta += len(encoded) - len(bytes.fromhex(item['source_hex']))
    if modified != ['journey_houses_line_013', 'journey_houses_line_023']:
        raise ValueError("Unexpected v09r2 dialogue modifications")
    if sum(a != b for a, b in zip(old, new)) != 40:
        raise ValueError("Unexpected event byte difference")
    return {
        'status': 'PASS',
        'scope': 'source-free static QA; not emulator validation',
        'v08_ips_records': len(base),
        'overlapping_rom_ranges': 0,
        'v09r2_patch_bytes': len(updated_patch),
        'translated_records_verified': len(items),
        'choice_records': sum(x['role'] == 'choice' for x in items),
        'dialogue_pages': len({x['page'] for x in items if x['role'] == 'dialogue'}),
        'revised_ids': modified,
        'decoded_event_bytes': len(new),
        'vm_control_words_preserved': True,
        'text_pages_and_choices_fit': True,
        'mGBA_test': 'PENDING',
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
