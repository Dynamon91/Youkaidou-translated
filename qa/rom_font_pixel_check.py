#!/usr/bin/env python3
"""Check real v0.8 8x16 GBA font pixels used in the v0.9r1 script.

Usage: python3 qa/rom_font_pixel_check.py '/path/to/Youkaidou (Japan).gba'
Does not emulate, modify, or distribute the original ROM.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_patch import make_font

SOURCE_SHA256 = "080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06"
PUNCT = {' ':0, '!':1, '"':2, "'":0x3B, '(':7, ')':8, '*':9, '+':0xA,
         ',':0x1E, '-':0xD, '/':0xF, ':':0x1A, '=':0x1D, '?':0x1F, '.':0x20}

def glyph_code(char):
    if char in PUNCT: return PUNCT[char]
    if 'A' <= char <= 'Z': return 0x21 + ord(char) - ord('A')
    if 'a' <= char <= 'z': return 0x320 + ord(char) - ord('a')
    if '0' <= char <= '9': return 0x10 + ord(char) - ord('0')
    raise ValueError("Unsupported glyph " + repr(char))

def pixels(font, glyph):
    origin = (glyph // 10) * 640 + (glyph % 10) * 32
    values = []
    for y in range(16):
        for x in range(8):
            b = font[origin + (y//8)*320 + (y%8)*4 + x//2]
            values.append((b >> 4) & 15 if x % 2 else b & 15)
    return values

def run(rom_path):
    source = rom_path.read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise SystemExit("Source ROM mismatch: expected clean AFUJ Japanese ROM")
    manifest = json.loads((ROOT / 'journey_houses_translations_v09r1.json').read_text(encoding='utf-8'))
    font = make_font(source)
    chars = set()
    for item in manifest['strings']:
        text = re.sub(r'\{PLAYER_NAME\}', '', item['english'])
        chars.update(text)
    results = []
    for c in sorted(chars):
        ink = sum(v in (1,2) for v in pixels(font, glyph_code(c)))
        results.append({'character':c, 'glyph_code':hex(glyph_code(c)),
                        'ink_pixels':ink, 'pass':c==' ' or ink>0})
    missing = [x for x in results if not x['pass']]
    print(json.dumps({'status':'PASS' if not missing else 'FAIL',
                      'unique_characters':len(results), 'missing':missing,
                      'fonts':'real 8x16 font pixels reconstructed from clean ROM and v08 builder',
                      'limitation':'Static glyph evidence, not emulator screenshot'}, indent=2))
    if missing: raise SystemExit(1)

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit("Usage: python qa/rom_font_pixel_check.py original.gba")
    run(Path(sys.argv[1]))
