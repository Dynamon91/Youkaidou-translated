# Youkaidou v0.9r1 — regression verification (2026-11-19)

This check was performed against the user's clean 8,388,608-byte AFUJ ROM. **Static verification only**, not an mGBA gameplay certification.

- Clean ROM SHA-256: `080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06`
- Standalone incremental patch: `Youkaidou_English_v09r1_journey_houses.ips` (2,915 bytes)
- Patch SHA-256: `e93985ac4b66c72f35ea1c48df312931b4c0677b1d8bf307400eb504ca086594`
- Verified Git object SHA-1: `def0df01026e121d10f0010ae3db341e7f475ad7`
- Static QA: PASS — 26/26 text records; 19 dialogue pages; three 2-item choice menus; 3 player-name substitutions; 216-pixel maximum line width.
- Asset/VM: 2,564 bytes decoded; 2,889 bytes compressed; 88 event-table entries relocated; two code pointers updated; LZSS and IPS round-trips passed.
- Patch footprint: 1,831 ROM bytes differ; changes confined to relocated event data and its two pointer references; GBA header and font/UI graphic regions unchanged by add-on.
- Negative controls **passed 5/5**: injected font-region corruption, dialogue overflow, unsupported glyph, mismatching localized asset, and event-pointer tampering were all rejected by the validator.

## Patch-path equivalence check

The 2,915-byte v0.9 add-on was applied to the clean ROM and then followed by the repository's 34-byte hotfix. The result was compared byte-for-byte against the clean ROM patched once with the direct v0.9r1 IPS: **identical output**, with only **16 ROM bytes** changed by the hotfix relative to the v0.9 build. The hotfix's SHA-256 was independently checked as `5147f6a8ded4d10c28ed6cb0fdaeadcb60cf655daebcd521079cdd54ab0668bc`.

## Applying the patch

1. Start with your own **clean** Japanese Youkaidou ROM (`AFUJ`).
2. Apply `Youkaidou_English_v08.ips` to that ROM.
3. Apply `Youkaidou_English_v09r1_journey_houses.ips` to the resulting ROM.
4. **Do not** stack the older v0.9 add-on or the v0.9→v0.9r1 hotfix onto the complete v0.9r1 IPS.

## Still pending (not tested)

- Actual mGBA playthrough with captures of all 19 dialogue pages, both branches of all 3 menus, and real player-name rendering.
- Scene transitions, palettes and sprites, battles, save and Continue, and regression against the stable v0.8 path.
- Full-game translation coverage remains unknown; the 26/26 count covers only this event asset, not the entire game.

The user-owned Japanese ROM is neither included nor published.
