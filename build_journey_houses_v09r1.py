#!/usr/bin/env python3
"""Build the v09r1 journey_houses add-on for the Youkaidou v08 English patch."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

from script_codec import localize_script

SOURCE_SHA256 = "080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06"


def make_ips(before, after):
    if len(before) != len(after):
        raise ValueError("This incremental IPS builder requires equal-size ROMs.")
    out = bytearray(b"PATCH")
    i = 0
    while i < len(after):
        if before[i] == after[i]:
            i += 1
            continue
        start = i
        last = i
        while i < len(after) and i - start < 65535:
            if before[i] != after[i]:
                last = i
            elif i - last >= 8:
                break
            i += 1
        end = last + 1
        out += start.to_bytes(3, "big")
        out += (end - start).to_bytes(2, "big")
        out += after[start:end]
        i = end
    return bytes(out) + b"EOF"


def apply_ips(source, patch):
    if patch[:5] != b"PATCH":
        raise ValueError("Invalid IPS header.")
    result = bytearray(source)
    pos = 5
    while patch[pos:pos + 3] != b"EOF":
        address = int.from_bytes(patch[pos:pos + 3], "big")
        size = int.from_bytes(patch[pos + 3:pos + 5], "big")
        pos += 5
        if size:
            result[address:address + size] = patch[pos:pos + size]
            pos += size
        else:
            count = int.from_bytes(patch[pos:pos + 2], "big")
            value = patch[pos + 2]
            pos += 3
            result[address:address + count] = bytes([value]) * count
    return bytes(result)


def build(rom_path, output_dir):
    source = rom_path.read_bytes()
    source_sha = hashlib.sha256(source).hexdigest()
    if source_sha != SOURCE_SHA256:
        raise SystemExit(
            "Wrong source ROM. Use the clean YOUKAIDOU AFUJ ROM listed in README.md."
        )

    manifest_path = Path(__file__).with_name("journey_houses_translations_v09r1.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packed, references, event_report, localized = localize_script(source, manifest)

    destination = int(manifest["destination_rom_offset"], 16)
    asset_offset = int(manifest["asset_rom_offset"], 16)
    if any(source[destination:destination + len(packed)]):
        raise SystemExit("The v09r1 destination region is not empty in the clean source ROM.")

    patched = bytearray(source)
    patched[destination:destination + len(packed)] = packed
    original_pointer = struct.pack("<I", 0x08000000 + asset_offset)
    new_pointer = struct.pack("<I", 0x08000000 + destination)
    for reference in references:
        if source[reference:reference + 4] != original_pointer:
            raise SystemExit("Source event pointer changed at " + hex(reference))
        patched[reference:reference + 4] = new_pointer

    allowed = [(destination, destination + len(packed))]
    allowed.extend((reference, reference + 4) for reference in references)
    changed = [
        index for index, (old, new) in enumerate(zip(source, patched))
        if old != new
    ]
    if any(not any(start <= index < end for start, end in allowed) for index in changed):
        raise SystemExit("The incremental patch changed bytes outside its declared ranges.")

    patch = make_ips(source, patched)
    if apply_ips(source, patch) != bytes(patched):
        raise SystemExit("IPS round-trip verification failed.")

    output_dir.mkdir(parents=True, exist_ok=True)
    patch_path = output_dir / "Youkaidou_English_v09r1_journey_houses.ips"
    localized_path = output_dir / "localized_journey_houses.bin"
    report_path = output_dir / "journey_houses_v09r1_validation.json"
    patch_path.write_bytes(patch)
    localized_path.write_bytes(localized)

    validation = {
        "stage": "v09r1 incremental event localization — journey_houses",
        "base_version": "v08",
        "application_order": "Apply Youkaidou_English_v08.ips first, then this add-on.",
        "source_rom_sha256": source_sha,
        "source_asset": event_report,
        "destination_rom_offset": hex(destination),
        "pointer_references_updated": [hex(reference) for reference in references],
        "changed_byte_count": len(changed),
        "allowed_changed_ranges": [
            {"start": hex(start), "end": hex(end)} for start, end in allowed
        ],
        "ips_sha256": hashlib.sha256(patch).hexdigest(),
        "ips_bytes": len(patch),
        "lzss_roundtrip_passed": True,
        "ips_roundtrip_passed": True,
        "control_words_preserved": True,
        "player_name_variable_preserved": True,
        "cell_budgets_passed": True,
        "incremental_scope_only": True,
        "emulator_verification": "pending"
    }
    report_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "patch": str(patch_path),
        "localized_asset": str(localized_path),
        "validation": str(report_path),
        "patch_bytes": len(patch),
        "patch_sha256": validation["ips_sha256"],
        "dialogue_lines": event_report["nonempty_english_lines"],
        "emulator_verification": "pending"
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "output-v09r1")
    args = parser.parse_args()
    build(args.rom, args.output)
