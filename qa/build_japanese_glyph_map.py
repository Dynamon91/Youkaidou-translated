#!/usr/bin/env python3
"""Reconstruct Japanese glyph IDs from aligned, transcribed event manifests.

No original ROM is required. This map is consistent source transcription
evidence, not visual or contextual certification of new Japanese dialogue.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = [
    "story_translations.json",
    "village_translations.json",
    "house_translations.json",
    "elder_story_translations.json",
    "return_translations.json",
    "shrine_translations.json",
    "supply_houses_translations.json",
    "supply_village_translations.json",
    "departure_houses_translations.json",
    "departure_village_translations.json",
    "journey_village_translations.json",
    "journey_houses_translations_v09r2.json",
    "cargo_road_translations.json",
    "cargo_report_translations.json",
    "cargo_village_translations.json",
]

def code_key(number):
    return "0x{:04x}".format(number)

def decode_words(raw_hex, glyphs):
    words = [word[0] for word in struct.iter_unpack("<H", bytes.fromhex(raw_hex))]
    result = []
    unknown = set()
    for word in words:
        entry = glyphs.get(code_key(word))
        if entry is None:
            unknown.add(word)
            result.append("[?{}]".format(code_key(word)))
        else:
            result.append(entry["character"])
    return {
        "japanese": "".join(result),
        "total_glyph_tokens": len(words),
        "mapped_glyph_tokens": len(words) - sum(1 for word in words if code_key(word) not in glyphs),
        "unmapped_glyph_codes": [code_key(x) for x in sorted(unknown)],
        "manual_context_review_required": True,
    }

def compile_map():
    mapping = {}
    occurrences = Counter()
    manifests = defaultdict(set)
    aligned_records = 0
    total_tokens = 0
    inventory = []
    for name in MANIFESTS:
        rows = json.loads((ROOT / name).read_text(encoding="utf-8"))["strings"]
        file_rows = 0
        file_tokens = 0
        for row in rows:
            if not row.get("source_hex") or not row.get("japanese"):
                continue
            chars = re.findall(r"\{[A-Z_]+\}|.", row["japanese"], flags=re.DOTALL)
            raw = bytes.fromhex(row["source_hex"])
            if len(raw) % 2:
                raise ValueError("Odd source_hex bytes: {} / {}".format(name, row["id"]))
            words = [w[0] for w in struct.iter_unpack("<H", raw)]
            if len(chars) != len(words):
                raise ValueError("Japanese / glyph mismatch: {} / {}".format(name, row["id"]))
            aligned_records += 1
            file_rows += 1
            total_tokens += len(words)
            file_tokens += len(words)
            for glyph, character in zip(words, chars):
                if glyph in mapping and mapping[glyph] != character:
                    raise ValueError("Conflicting glyph {}: {} vs {}".format(code_key(glyph), mapping[glyph], character))
                mapping[glyph] = character
                occurrences[glyph] += 1
                manifests[glyph].add(name)
        inventory.append({"path": name, "aligned_records": file_rows, "aligned_glyph_tokens": file_tokens})
    glyphs = {code_key(g): {
        "character": mapping[g],
        "occurrences": occurrences[g],
        "source_manifests": sorted(manifests[g]),
    } for g in sorted(mapping)}
    return {
        "format": "youkaidou_ja_glyph_map_v1",
        "manifest_count": len(MANIFESTS),
        "aligned_records": aligned_records,
        "aligned_glyph_tokens": total_tokens,
        "unique_glyph_codes": len(glyphs),
        "conflicts": 0,
        "manifest_inventory": inventory,
        "glyphs": glyphs,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="Check committed map against manifests")
    p.add_argument("--output", type=Path, default=ROOT / "qa/japanese_glyph_map.json")
    args = p.parse_args()
    output = compile_map()
    if args.check:
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        for field in ("format", "manifest_count", "aligned_records", "aligned_glyph_tokens", "unique_glyph_codes", "conflicts", "manifest_inventory", "glyphs"):
            if existing.get(field) != output[field]:
                raise SystemExit("FAIL: glyph map differs at {}".format(field))
        print("PASS: {} records, {} tokens, {} glyphs, no conflicts".format(
            output["aligned_records"], output["aligned_glyph_tokens"], output["unique_glyph_codes"]))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Wrote", args.output)

if __name__ == "__main__":
    main()
