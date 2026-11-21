#!/usr/bin/env python3
"""Discover probable untranslated event scripts in a user-owned clean AFUJ ROM.

Only local metadata / source glyph IDs are written. This is not a translator,
and the scan does not establish in-game playability.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from script_codec import decode_lzss

SOURCE_SHA256 = '080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06'
POINTER_WINDOWS = ((0x15E000, 0x161000), (0x76E000, 0x76F000))
RESOURCE_START, RESOURCE_END = 0x700000, 0x770000


def extract_slots(decoded, code_base):
    """Locate probable 0x4003 (choice) and 0x4005 (dialogue) print slots."""
    slots = []
    for pos in range(code_base, len(decoded) - 3, 2):
        marker = struct.unpack_from('<H', decoded, pos)[0]
        if marker not in (0x4003, 0x4005):
            continue
        start = pos + 2
        end = start
        while end + 1 < len(decoded):
            word = struct.unpack_from('<H', decoded, end)[0]
            if word >= 0x4000:
                break
            end += 2
        if end <= start or end == len(decoded):
            continue
        slots.append({
            'offset': hex(start),
            'marker': hex(marker),
            'role': 'choice' if marker == 0x4003 else 'dialogue',
            'source_hex': decoded[start:end].hex(),
            'source_codepoint_count': (end - start) // 2,
            'max_cells': 18 if marker == 0x4003 else 27,
            'japanese': None,
            'english': None,
            'status': 'UNTRANSCRIBED — verify Japanese glyphs and context',
        })
    return slots


def known_assets(root):
    known = {}
    for path in root.glob('*translations*.json'):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            continue
        if 'asset_rom_offset' in data:
            known.setdefault(int(data['asset_rom_offset'], 16), []).append(path.name)
    return known


def discover(rom, known):
    """Find candidate GBA event references in the verified code/pointer windows."""
    refs = {}
    for first, end in POINTER_WINDOWS:
        for address in range(first, min(end, len(rom) - 3), 4):
            value = struct.unpack_from('<I', rom, address)[0]
            destination = value - 0x08000000
            if RESOURCE_START <= destination < RESOURCE_END:
                refs.setdefault(destination, []).append(address)
    events = []
    for off in sorted(refs):
        if off + 4 > len(rom):
            continue
        size = int.from_bytes(rom[off:off + 4], 'big')
        if not (128 <= size <= 0x10000):
            continue
        try:
            raw, after = decode_lzss(rom, off, max_output=0x10000)
            if len(raw) < 16:
                continue
            first, second, base, code_size = struct.unpack_from('<4I', raw)
            if not (first == 16 and first <= second <= base
                    and (second - first) % 4 == 0
                    and (base - second) % 4 == 0
                    and base + code_size == len(raw)):
                continue
            offsets = struct.unpack_from('<' + 'I' * ((base - first) // 4), raw, first)
            if any(idx >= code_size for idx in offsets):
                continue
            slots = extract_slots(raw, base)
            events.append({
                'asset_rom_offset': hex(off),
                'status': 'known' if off in known else 'candidate_untranslated',
                'known_manifests': known.get(off, []),
                'decoded_sha256': hashlib.sha256(raw).hexdigest(),
                'source_decoded_bytes': len(raw),
                'source_header': [first, second, base, code_size],
                'reference_offsets': [hex(p) for p in refs[off]],
                'pointer_references': len(refs[off]),
                'event_table_entries': len(offsets),
                'probable_text_slots': len(slots),
                'slots': slots,
                'requires_review': True,
            })
        except (ValueError, AssertionError, struct.error, IndexError, OverflowError):
            continue
    return events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path, help='Clean Japanese YOUKAIDOU .gba (AFUJ)')
    parser.add_argument('--output', type=Path, default=Path('event_candidates_local.json'))
    parser.add_argument('--untranslated-only', action='store_true')
    parser.add_argument('--after', type=lambda x: int(x, 0), default=0x70BBFA)
    args = parser.parse_args()
    source = args.rom.read_bytes()
    if len(source) != 0x800000 or hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        parser.error('Requires verified clean AFUJ ROM (8,388,608 bytes)')
    results = discover(source, known_assets(ROOT))
    if args.untranslated_only:
        results = [r for r in results if r['status'] == 'candidate_untranslated']
    results = [r for r in results if int(r['asset_rom_offset'], 16) > args.after]
    payload = {
        'status': 'SOURCE EXTRACTION ONLY',
        'note': 'Glyph IDs must be transcribed and translated manually; none are auto-approved.',
        'events': results,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'candidates': len(results), 'output': str(args.output),
        'candidate_offsets': [r['asset_rom_offset'] for r in results],
    }, indent=2))


if __name__ == '__main__':
    main()
