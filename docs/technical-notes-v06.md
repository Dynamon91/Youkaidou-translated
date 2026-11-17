# Youkaidou English v06 — technical notes

The new batch localizes four event assets: the village before and after accepting
the delivery-route mission, and their house conversations. It fills 140 nonempty
English text slots across 83 dialogue pages and eight choice menus.

| Scenario | Dialogue pages checked | Menus checked with both selections |
| --- | --- | --- |
| supply village | 9 / 14 | 1 / 1 |
| supply houses | 21 / 34 | 3 / 4 |
| departure village | 6 / 16 | 1 / 1 |
| departure houses | 8 / 19 | 1 / 2 |

The remaining 39 pages and two menus retain source, variable, encoding, and width
checks. Per-page and per-record status appears in `mission_pixel_checks.json` and
the four translation manifests. Brief confirmation lines and conditional Yayoi
variants are among the pending pages. Later chapters are still untranslated.

All checked captures match the final ROM's 8x16 glyph ink exactly. Dialogue keeps
two lines of at most 27 cells / 216 pixels. Choice captions have an 18-cell limit.
Each player-name variable stays in its original text slot with an eight-cell
budget. VM commands, branch entries, control words, and variable words are retained.

The 188 earlier dialogue-page captures, 22 earlier choice captures, and seven
level-up messages are retained with their original provenance. Their event assets
and both font banks are byte-identical in v06. All archived screenshots were
checked again against the final font pixels; earlier gameplay was not all replayed.
The complete included set contains 232 dialogue pages and 34 choice captures.

The UI batch remains at 85 records: 51 have observed screen checks, and 34 have
static checks only. The earlier pending branches remain listed in their reports.

`しおり` is a **bookmark** used to select participating yokai. It is distinct from
the `おふだ` **talismans** grid. `どうぐ` matches **Items**, `けいけんち` is **EXP**,
and `かいふくやく` is healing medicine. The new source glyphs were read from the
original font; Japanese source and English review text are preserved in
`verification/v06/translation_review.txt`.

Normal controls and emulator checkpoints reached the recorded branches. No
gameplay data was edited. After accepting the mission, cancellation, a completed
8192-byte save, reset, Continue, and overwrite cancellation passed. Continued
Yayoi dialogue matched the departure scenario, proving the mission flag survived.
A separate real v05 save loaded in v06 after reset and retained its shrine-report
stage, with Yayoi's English dialogue also pixel checked.

Verification uses mGBA 0.10.5 at 240x160. Native screenshots and JSON reports are
included. The preview scales actual captures by 3x without smoothing. The v06
test save and harness sources are under `verification/v06/`; harness paths refer
to the original workspace and require adaptation for a local replay.

The builder requires the exact original ROM specified in the main README. It
rebuilds nine event assets, rebases 805 event/branch entries, and redirects 1284
asset references. All decoded events fit their 64 KiB event-data area. Applying
the IPS reproduces the output ROM byte for byte. The delivered source ZIP was
rebuilt independently and matched the release ROM and patch.

To check archived screenshot pixels after building, install Pillow, copy
`rebuilt/Youkaidou_English_v06.gba` beside `check_captures.py`, and run:

```sh
python3 check_captures.py
```

This checks the included captures; it does not replay gameplay. Link connectivity,
later battles/menus, late-game saves, and physical hardware remain unverified.
No full-game completion percentage is claimed. ROM files are not tracked in Git.
