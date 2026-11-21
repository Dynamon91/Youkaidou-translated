# Next-event extraction — development milestone

The development branch now includes a guarded script scanner to continue translation **beyond** the fully translated `journey_houses` event asset (current add-on: **26 text slots, 19 dialogue pages and 3 choice menus**).

## Why extraction is separate from translation

The original Japanese GBA ROM is not stored in this repository. The source-free tests can confirm the existing IPS and event data, but they cannot discover additional story dialogue from the game without the user's clean original. Guessing a source pointer or substituting fabricated Japanese text would risk corrupting the game.

The next step is **source inventory**, not publication of an unverified patch. The scanner identifies probable new LZSS-compressed event assets referenced by the GBA engine and emits a *local* JSON file of raw two-byte text-code sequences, with original marker offsets and pointer references. Source glyph codes must subsequently be decoded/transcribed and interpreted in story context.

## Commands

Run from the repository root using Python 3.8+:

```sh
python3 qa/audit_v09r2_patch.py
python3 qa/test_discover_next_events.py
python3 qa/discover_next_events.py "/path/to/Youkaidou (Japan).gba" --untranslated-only --output event_candidates_local.json
```

The scanner checks for a **clean unmodified** 8,388,608-byte Japanese `AFUJ` ROM. Required SHA-256:

```
080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06
```

Default scan threshold is after source asset offset `0x70BBFA` (the current journey-and-houses event). It examines only established event-pointer windows (`0x15E000–0x161000`, `0x76E000–0x76F000`) and checks LZSS, header layout and table entries. This scoped scan may **miss** assets referenced differently: no claim of full-game coverage is made.

Review `event_candidates_local.json` locally. The scanner deliberately marks each English/Japanese transcription as `null` rather than inventing text. The result is **not** a finished patch, and probable slots may include false positives. Leave extracted commercial source content local rather than committing the ROM or raw dumps to public GitHub.

## Quality gates for the next translation

1. Verify the actual Japanese text and its speaker/context from ROM evidence and, where necessary, gameplay.
2. Translate while preserving `{PLAYER_NAME}`, event control words and narrative tone.
3. Respect **27 dialogue cells / 18 choice cells** and test the exact 8-pixel font.
4. Build a new incremental IPS with disjoint write ranges; test compression, pointers and source SHA-256.
5. Capture actual mGBA screenshots for all new pages and both responses in each choice menu, then check scene transitions, save/Continue and sprite/palette integrity.
6. Keep stable `main` unchanged until gameplay checks pass.

## Current verification boundary

An independent source-free audit of the actual files confirmed **271 base IPS records, zero overlapping write ranges, all 26 translated text slots matching the embedded event data, unchanged event tables/control words, and no static textbox overflows**. See [the 21 November 2026 audit](../verification/v09r2/extended_static_audit_2026-11-21.json).

The local synthetic scanner fixture passed. The new in-repository Python test and validator are published for reproducibility, but **no new ROM-driven chapter extraction or mGBA verification was performed**.
