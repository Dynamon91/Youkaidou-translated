# Youkaidou v0.9 development — journey_houses

## Status

This is a development add-on built on the v0.8 English translation. The v0.8 release on `main` remains unchanged.

- 26 non-empty text records translated and encoded; a source scan confirms all 26 print/choice slots are covered.
- 19 dialogue pages and 3 choice menus included.
- Player-name variable slots retained.
- 88 event-table entries checked during relocation.
- Original VM control words preserved.
- LZSS decompression/recompression round-trip passed.
- IPS apply/round-trip passed.
- All dialogue and choice text stays within the original 27-cell / 18-cell limits.
- The localized asset is 2,564 decoded bytes and 2,889 compressed bytes at ROM offset `0x7c4000`.
- The v0.8 IPS range audit found no overlap with the v0.9 add-on's three write ranges.
- **mGBA gameplay verification is still pending.** Do not treat this as a fully tested release or merge it into `main` yet.

## Files

- `journey_houses_translations.json` — source-aligned Japanese/English records and ROM offsets.
- `build_journey_houses_v09.py` — reproducible add-on patch builder.
- `Youkaidou_English_v09_journey_houses.ips` — incremental IPS patch.
- `verification/v09/journey_houses_static_validation.json` — compact validation record.

## Required ROM and patch order

The builder accepts only the clean Japanese `YOUKAIDOU` GBA ROM, game code `AFUJ`, 8,388,608 bytes, SHA-256:

`080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06`

Build from the clean source:

```sh
python3 build_journey_houses_v09.py "/path/to/Youkaidou (Japan).gba" --output rebuilt
```

For playtesting, apply the patches in this order:

1. Apply `Youkaidou_English_v08.ips` to the clean Japanese ROM.
2. Apply `Youkaidou_English_v09_journey_houses.ips` to that v0.8 result.

The v0.9 patch is an add-on, not a replacement for v0.8. The original ROM is not included in this repository.

## Change scope

The add-on writes the relocated event asset at `0x7c4000–0x7c4b49` and updates two pointer references at `0x15e8e0–0x15e8e4` and `0x76e174–0x76e178`. No other ROM bytes are changed by this patch.

The v0.8 IPS was parsed as 271 records (140,800 bytes); none intersect these v0.9 ranges. The generated v0.9 IPS is 2,915 bytes with SHA-256:

`6b2b8e98a9f846b992dad2b8cdb8d98022c44cf4cb0792f5e3919eb37edb7b54`

## Next verification work

1. Run the v0.8 + v0.9 patch in mGBA.
2. Capture the 19 dialogue pages and all three choice menus, selecting both responses where applicable.
3. Verify player-name substitution, scene transitions, save/continue and event progression.
4. Fix any clipping, timing, control-flow or state issues before promoting the build.

Static encoding checks are not a substitute for an emulator playthrough.
