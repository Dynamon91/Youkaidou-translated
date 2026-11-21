# Next-event extraction — development milestone

The development branch now includes a guarded script scanner to continue translation **beyond** the fully translated `journey_houses` event asset (current add-on: **26 text slots, 19 dialogue pages and 3 choice menus**).

## Why extraction is separate from translation

The original Japanese GBA ROM is not stored in this repository. The source-free tests can confirm the existing IPS and event data, but they cannot discover additional story dialogue from the game without the user's clean original. Guessing a source pointer or substituting fabricated Japanese text would risk corrupting the game.

The next step is **source inventory**, not publication of an unverified patch. The scanner identifies probable new LZSS-compressed event assets referenced by the GBA engine and emits a *local* JSON file with original marker offsets, pointer references, source text-code sequences, and **draft Japanese text decoded through the recovered glyph map**. Unknown codes are marked `[?0xNNNN]` and never guessed. Source glyph mappings and dialogue context must still be visually checked before a translation is accepted.

## New Japanese glyph map

The [reproducible map](../qa/japanese_glyph_map.json) was compiled from **15 previously transcribed original-script manifests**. Across **608 non-empty source-aligned records and 9,605 glyph tokens**, it derives **326 distinct source glyph code → Japanese character mappings, with zero internal conflicts**. The player-name token `0x1000` is kept as `{PLAYER_NAME}`. A Japanese character can map to more than one glyph code (for example `間`), so the decoder uses **code-to-character** rather than assuming a one-to-one inverse.

The map is drawn from existing project transcription data, not independently certified against every original Japanese glyph bitmap. It can reduce manual transcription effort for later chapters, but must not be mistaken for full-game coverage or final dialogue verification.

Rebuild/check and test without a ROM:

```sh
python3 qa/build_japanese_glyph_map.py --check
python3 qa/test_japanese_glyph_map.py
python3 qa/test_discover_next_events.py
```

The decoder's `japanese` result is a **draft**. An untranslated asset may contain glyph codes not in the map; those remain visible as unknowns, and any completed Japanese lines still require contextual review. Existing English v0.9r2 IPS data is unchanged.

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

Review `event_candidates_local.json` locally. The scanner leaves every English translation as `null` and offers **draft mapped Japanese text** only where a glyph code is known. Unmapped glyphs are explicit placeholders. The result is **not** a finished patch, and probable slots may include false positives. Leave extracted commercial source content local rather than committing the ROM or raw dumps to public GitHub.

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
