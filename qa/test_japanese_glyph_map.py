#!/usr/bin/env python3
"""ROM-free regression tests for aligned Japanese text-code mappings."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qa"))
from build_japanese_glyph_map import compile_map, decode_words, MANIFESTS, code_key


def main():
    actual = compile_map()
    reference = json.loads((ROOT / "qa/japanese_glyph_map.json").read_text(encoding="utf-8"))
    assert actual == reference, "Tracked manifests and generated map differ"
    assert len(MANIFESTS) == 15
    assert actual["aligned_records"] == 608
    assert actual["aligned_glyph_tokens"] == 9605
    assert actual["unique_glyph_codes"] == 326
    assert actual["glyphs"]["0x1000"]["character"] == "{PLAYER_NAME}"
    assert actual["glyphs"]["0x0000"]["character"] == "　"
    assert actual["glyphs"]["0x0303"]["character"] == "妖"

    examined = 0
    for name in MANIFESTS:
        for item in json.loads((ROOT / name).read_text(encoding="utf-8"))["strings"]:
            if not item.get("source_hex") or not item.get("japanese"):
                continue
            decoded = decode_words(item["source_hex"], actual["glyphs"])
            assert decoded["unmapped_glyph_codes"] == [], (name, item["id"])
            assert decoded["japanese"] == item["japanese"], (name, item["id"])
            assert decoded["mapped_glyph_tokens"] == decoded["total_glyph_tokens"]
            examined += 1
    assert examined == 608, examined
    unknown = decode_words("ffff", actual["glyphs"])
    assert unknown["unmapped_glyph_codes"] == ["0xffff"]
    assert unknown["japanese"] == "[?0xffff]"
    assert unknown["mapped_glyph_tokens"] == 0
    print("PASS: {} source records decoded exactly; {} glyphs; unknown codes remain explicit".format(
        examined, len(actual["glyphs"])))


if __name__ == "__main__":
    main()
