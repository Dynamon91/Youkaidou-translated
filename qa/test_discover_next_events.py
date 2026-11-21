#!/usr/bin/env python3
"""Synthetic scanner tests. Does not read or embed a commercial GBA ROM."""
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from script_codec import encode_lzss_literals
from discover_next_events import discover

def main():
    rom = bytearray(0x800000)
    off = 0x70C000
    code = bytes.fromhex('054021000200 034003000140') + bytes.fromhex('0140') * 50
    script = struct.pack('<4I', 16, 20, 24, len(code)) + struct.pack('<2I', 0, 0) + code
    rom[off:off + len(encode_lzss_literals(script))] = encode_lzss_literals(script)
    for ref in (0x15E020, 0x76E120):
        struct.pack_into('<I', rom, ref, 0x08000000 + off)
    events = discover(rom, {})
    assert len(events) == 1, events
    event = events[0]
    assert event['status'] == 'candidate_untranslated'
    assert event['pointer_references'] == 2
    assert event['asset_rom_offset'] == '0x70c000'
    assert len(event['slots']) == 2, event['slots']
    assert event['slots'][0]['source_hex'] == '21000200'
    assert event['slots'][0]['role'] == 'dialogue'
    assert event['slots'][1]['source_hex'] == '0300'
    assert event['slots'][1]['role'] == 'choice'
    assert event['slots'][1]['english'] is None
    assert discover(rom, {off: ['known.json']})[0]['status'] == 'known'
    rom[off:off + 4] = b'\xff\xff\xff\xff'
    assert discover(rom, {}) == []
    print('PASS: synthetic event discovery, 2 pointer refs, 2 slots, known-asset skip, bad header rejection')

if __name__ == '__main__':
    main()
