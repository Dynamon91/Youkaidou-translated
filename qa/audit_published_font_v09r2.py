#!/usr/bin/env python3
"""ROM-free glyph coverage audit using the *published* v0.8 IPS font bytes.

This does not certify emulator rendering, palette selection or visual aesthetics.
Unknown font bytes are INCONCLUSIVE, not silently treated as blank or present.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_patch import FONT_DEST, FONT_SIZE, LOWERCASE_START
from qa.audit_v09r2_patch import ips_records

FONT_TOTAL = max(FONT_SIZE // 640, (LOWERCASE_START + 26 + 9) // 10) * 640
MANIFEST = ROOT / 'journey_houses_translations_v09r2.json'
IPS = ROOT / 'Youkaidou_English_v08.ips'


def glyph_index(char):
    if 'A' <= char <= 'Z':
        return 0x21 + ord(char) - ord('A')
    if 'a' <= char <= 'z':
        return LOWERCASE_START + ord(char) - ord('a')
    if '0' <= char <= '9':
        return 0x10 + ord(char) - ord('0')
    return {' ': 0, '!': 1, '"': 2, "'": 0x3B, '(': 7, ')': 8,
            '*': 9, '+': 10, ',': 30, '-': 13, '/': 15,
            ':': 26, '=': 29, '?': 31, '.': 32}[char]


def ink_from_ips(font, known, code):
    origin = (code // 10) * 640 + (code % 10) * 32
    if origin + 328 > len(font):
        return {'result': 'FAIL', 'reason': 'glyph outside font allocation'}
    inks = 0
    missing = 0
    for y in range(16):
        for x in range(0, 8, 2):
            pos = origin + (y // 8) * 320 + (y % 8) * 4 + x // 2
            if not known[pos]:
                missing += 2
                continue
            byte = font[pos]
            inks += (byte & 15) in (1, 2)
            inks += (byte >> 4) in (1, 2)
    if missing:
        return {'result': 'INCONCLUSIVE', 'unknown_pixels': missing, 'known_ink_pixels': inks}
    return {'result': 'PASS' if inks else 'FAIL', 'ink_pixels': inks}


def audit():
    font = bytearray(FONT_TOTAL)
    known = bytearray(FONT_TOTAL)
    for offset, data in ips_records(IPS.read_bytes()):
        start = max(offset, FONT_DEST)
        end = min(offset + len(data), FONT_DEST + FONT_TOTAL)
        if start < end:
            n = end - start
            font[start - FONT_DEST:end - FONT_DEST] = data[start - offset:start - offset + n]
            known[start - FONT_DEST:end - FONT_DEST] = b'\x01' * n
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    chars = set()
    for item in manifest['strings']:
        chars.update(re.sub(r'\{PLAYER_NAME\}', '', item['english']))
    results = {}
    for char in sorted(chars):
        if char == ' ':
            continue
        results[char] = ink_from_ips(font, known, glyph_index(char))
    failures = {k:v for k,v in results.items() if v['result'] == 'FAIL'}
    unknown = {k:v for k,v in results.items() if v['result'] == 'INCONCLUSIVE'}
    return {
        'status': 'FAIL' if failures else 'INCONCLUSIVE' if unknown else 'PASS',
        'scope': 'Published IPS font tile ink coverage; not emulator verification',
        'unique_characters': len(chars),
        'glyphs_checked_excluding_space': len(results),
        'known_font_bytes': sum(known),
        'font_allocation_bytes': FONT_TOTAL,
        'new_uppercase': {k: results[k] for k in ('D', 'O', 'K')},
        'failed': failures,
        'inconclusive': unknown,
        'emulator_test': 'PENDING',
    }


if __name__ == '__main__':
    report = audit()
    print(json.dumps(report, indent=2))
    if report['status'] == 'FAIL':
        raise SystemExit(1)
    if report['status'] == 'INCONCLUSIVE':
        raise SystemExit(2)
