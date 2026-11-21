# Youkaidou — English translation

A work-in-progress English fan translation of **Youkaidou for Game Boy Advance**.

Current stable release: **v08**. A separate development branch, **v0.9-journey-houses**, contains the next incremental dialogue update.

## Japanese decoder milestone — 326 original glyph codes (21 November 2026)

The development branch now contains a **reproducible Japanese glyph-code decoder** compiled from 15 earlier, transcribed scenario manifests. Across **608 aligned records (9,605 original glyph positions)**, it identified **326 code-to-character mappings with zero internal conflicts**. The special `{PLAYER_NAME}` script variable remains distinct from ordinary text.

- [Japanese glyph map](qa/japanese_glyph_map.json) and [deterministic map compiler](qa/build_japanese_glyph_map.py).
- [Decoded text regression tests](qa/test_japanese_glyph_map.py): round-trip all 608 Japanese source records and require unknown glyphs to stay visible.
- [Next-event extractor](qa/discover_next_events.py): can now emit **draft Japanese text** alongside the raw glyph IDs for later event candidates when a clean original ROM is supplied.
- [GitHub Actions source-free CI](.github/workflows/static-translation-qa.yml): [successful run](https://github.com/Dynamon91/Youkaidou-translated/actions/runs/44917188636) confirms v0.9r2 IPS reproducibility, 608-string map round-trip, synthetic event parsing and script/IPS regression.

**Current patch remains v0.9r2; no additional chapter has been translated in this milestone.** Source transcriptions and automated checks are not substitutes for the Japanese game context, accurate in-game font pixels or mGBA gameplay captures. Original Japanese GBA ROM is not published. See [next-event instructions](docs/next-event-extraction.md).

### Font graphics regression check (21 November 2026)

The new [ROM-free IPS font coverage audit](qa/audit_published_font_v09r2.py) examines the **actual font tile bytes present in the published v0.8 IPS**, then checks all printable glyphs used by the v0.9r2 dialogue, including newly introduced uppercase `D`, `O` and `K`. Unlike the older ROM-dependent font reconstruction check, this can run in GitHub Actions without a game ROM.

Run `python3 qa/audit_published_font_v09r2.py`. It distinguishes **PASS** (known glyph pixels have ink), **FAIL** (fully known glyph is blank) and **INCONCLUSIVE** (patch lacks bytes needed to decide). The automated workflow now includes this check. It is **not** an emulator graphics certification; palette selection, text position, transitions and on-screen rendering still require mGBA screenshots.

## Continued work — verification and next-event discovery (21 November 2026)

The latest **v0.9r2** English patch was re-audited against the existing **v0.8** IPS: all 26 encoded strings were found in the event data, the 271 v0.8 IPS records have **zero overlapping write ranges** with the add-on, and event tables and VM commands remain intact. See [extended static audit](verification/v09r2/extended_static_audit_2026-11-21.json).

New tools:
- [Source-free v0.9r2 IPS and text validator](qa/audit_v09r2_patch.py) — `python3 qa/audit_v09r2_patch.py`.
- [Next-event candidate extractor](qa/discover_next_events.py) and [synthetic test](qa/test_discover_next_events.py).
- [Instructions and emulator quality gates](docs/next-event-extraction.md).

**Scope:** The scanner is ready for the next Japanese event assets, but this session did not have access to the clean AFUJ ROM. **No further chapter has yet been translated or emulator-verified.** Stable v0.8 on `main` is unchanged. The development patch remains v0.9r2.

## v0.9r2 development translation refinement (21 November 2026)

Two contextual English improvements are now available on this branch, without changing text-cell counts: `Tomi: Do take care...` and `Yayoi: Goofing off? You OK?`. The journey-and-houses section still covers **26/26 strings, 19 dialogue pages and 3 choice menus**.

**Direct patch:** [Download v0.9r2 IPS](Youkaidou_English_v09r2_journey_houses.ips). Apply **v0.8 first**, then this v0.9r2 IPS; **do not apply v0.9r1 or other journey-houses patches after it**. [Read the translation and static QA notes](docs/v09r2-fidelity.md). The reproducible build is in `qa/build_v09r2_from_v09r1.py` and does not require distributing an original ROM.

This is a **development patch**. mGBA captures, on-screen clipping, menu behavior, transitions, save and Continue remain **unverified**. Stable `main` stays at v0.8. Earlier v0.9r1 documentation is retained for history.

## Current progress

- The delivery rescue is won and the ride home, elder report and next quest
  are now verified in the game. All six menus in this batch were checked with
  both replies selected, including both village rest choices.
- **106 of 116 dialogue pages** in the 186-line batch pass exact screen checks,
  up from six checked pages in v07. Ten conditional or unvisited pages remain.
- New in v08: **HP Med** fits the inventory's original six-character space.
  Normal item use still restores HP. Two elder lines were also corrected.
- Saving and Continue preserve the next quest. A real v07 save also loads
  correctly. The complete evidence set covers **338 dialogue pages, 46 choice
  captures, seven level-up messages and five item checks**.
- This is still a partial translation. Later chapters and some UI remain
  Japanese. Pending checks are listed in the reports.


## New v0.9r1 patch-font preview gallery (static QA)

[View the four new ROM-font preview images](docs/v09r1-font-qa-and-previews.md) and [pixel-glyph coverage report](verification/v09r1/rom_font_pixel_coverage.json). The preview images use the actual v0.8 English GBA font bitmaps and v0.9r1 translation strings. **47 unique glyphs, including space, were checked; none are missing.** A [reproducible font pixel check script](qa/rom_font_pixel_check.py) is included.

**Important:** These are reconstructed, diagnostic text-layout previews, **not actual gameplay or mGBA screenshots**. The game graphics, choice behavior, save/load and page transitions still require emulator review.

## v0.9r1 development update — graphics preflight and text fidelity

The branch now includes a verified 34-byte [v0.9 → v0.9r1 hotfix](Youkaidou_v09_to_v09r1_text_hotfix.ips) for one Yayoi line, plus a new [v0.9r1 translation manifest](journey_houses_translations_v09r1.json), [direct-patch builder](build_journey_houses_v09r1.py), [static graphics integrity report](verification/v09r1/graphics_preflight.json) and [emulator screenshot acceptance checklist](docs/visual-review-v09r1.md).

The contextual correction restores Yayoi's question about joking: `Yayoi: Joking? Really okay?` (27 cells). The patch does **not** modify font bitmaps, background tiles, menu assets or the GBA ROM header; the 19 dialogue pages and three choice menus satisfy static cell-budget checks. **Real mGBA visual/gameplay verification is pending.**

**Recommended direct patch:** [Download Youkaidou English v0.9r1 IPS](Youkaidou_English_v09r1_journey_houses.ips) (**2,915 bytes**, SHA-256 `e93985ac4b66c72f35ea1c48df312931b4c0677b1d8bf307400eb504ca086594`). First apply [v0.8](Youkaidou_English_v08.ips) to your clean `AFUJ` ROM, then apply this v0.9r1 IPS. **Do not also apply v0.9 or the 34-byte hotfix.** This is a development patch: mGBA screenshots, menu selection and save/continue checks are pending.

**Verified file integrity:** this standalone GitHub IPS has Git blob SHA `def0df01026e121d10f0010ae3db341e7f475ad7` matching the locally validated build. [Static and negative-test log](verification/v09r1/static_regression_2026-11-19.md).

**Patch order using the files hosted here:** clean AFUJ ROM → v08 IPS → v09 Journey & Houses IPS extracted from the [v09 package](Youkaidou_v09_Journey_Houses_Package.zip) → [v09r1 hotfix](Youkaidou_v09_to_v09r1_text_hotfix.ips). Alternatively, use the direct v09r1 patch generated by the new builder *instead of* v09 plus hotfix. Never stack the direct v09r1 patch on top of v09.

## v0.9 development update — journey and houses

The [v0.9 development branch](https://github.com/Dynamon91/Youkaidou-translated/tree/v0.9-journey-houses)
adds **26 translated text records across 19 dialogue pages and 3 choice menus**.
Player-name variables and original event control flow are preserved. Static
layout, LZSS and IPS round-trip checks pass. The add-on's ROM write ranges were
checked against the v08 patch; there are no overlapping records.

**Gameplay verification is pending.** This branch is not yet a replacement for
the v08 release and should not be merged into `main` until mGBA testing passes.

- [Download the complete v0.9 package ZIP](https://github.com/Dynamon91/Youkaidou-translated/raw/refs/heads/v0.9-journey-houses/Youkaidou_v09_Journey_Houses_Package.zip)
- [v0.9 translation manifest](journey_houses_translations.json)
- [v0.9 technical notes](docs/technical-notes-v09-journey-houses.md)
- [v0.9 static validation report](verification/v09/journey_houses_static_validation.json)

**Patch order:** apply the v08 IPS to the clean Japanese ROM first, then apply
the v0.9 journey-and-houses add-on.

## Screenshots from the working translation

Real emulator captures of the driver's train problem and the elder's warning,
enlarged without smoothing:

![v08 driver and elder dialogue](Youkaidou_English_v08_Preview.png)

The translated medicine name in the working inventory:

![HP Med inventory name](screenshots/items-v08/final-medicine-name.png)

## Try v08

[Download the v08 IPS patch](https://github.com/Dynamon91/Youkaidou-translated/raw/refs/heads/main/Youkaidou_English_v08.ips)
and apply it to the clean Japanese ROM with an IPS patcher.

Required original: `YOUKAIDOU`, game code `AFUJ`, 8,388,608 bytes.
SHA-256: `080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06`.
Apply the patch to the clean original, not an earlier English build.

To build v08 from source with Python 3.8 or newer:

```sh
python3 build_patch.py "/path/to/Youkaidou (Japan).gba" --output rebuilt
```

For the v0.9 add-on build, see
[the v0.9 technical notes](docs/technical-notes-v09-journey-houses.md).

The repository contains translation files, patch builders, IPS patches and
screenshot evidence. See [v08 technical notes](docs/technical-notes-v08.md)
for the detailed checks and remaining work.
