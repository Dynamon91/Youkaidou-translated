# Youkaidou — v0.9r2 English fidelity improvement

Development branch: `v0.9-journey-houses`. This is an incremental patch on top of stable **v0.8**.

## Translation revisions

| Japanese source | Prior English | Revised English | Fit |
|---|---|---|---|
| トミさん：「体に気をつけてね・・・」 | Tomi: Stay healthy... | **Tomi: Do take care...** | 21/27 cells |
| やよい：「そんなにふざけていて本当に大丈夫？」 | Yayoi: Joking? Really okay? | **Yayoi: Goofing off? You OK?** | 27/27 cells |

The new wording better preserves the speakers' concern: Tomi's caring send-off and Yayoi's doubt about the protagonist fooling around. These changes do **not** add new text slots. Total coverage is still 26 records, 19 pages and 3 two-answer choice menus for this specific event asset.

## Reproduction and verification

```sh
python3 qa/build_v09r2_from_v09r1.py
```

The deterministic builder reads the existing, SHA-256-pinned v0.9r1 patch, extracts and decodes its relocated LZSS script asset, re-encodes these two **same-length** strings, and rewrites only the event-data IPS record. No Japanese ROM is required for rebuilding the patch. It validates the event tables, VM control words, exact text locations, LZSS round-trip and IPS record footprint. See [static regression JSON](../verification/v09r2/text_revision_static.json).

To play: **clean Japanese AFUJ ROM → v0.8 IPS → direct v0.9r2 IPS**. Do not stack v0.9r1, v0.9 or either hotfix on top of the direct patch.

**Graphics caution:** No font tiles, palettes, sprite graphics, GBA header, event pointers or UI assets were altered by the v0.9r2 revision. This static property is *not* proof of error-free graphics. The new revision **has not been tested in mGBA**. Capture all 19 text pages, 3 menus (both choices), transitions and save/continue before promoting to the stable branch.

Actual v0.8 screenshots remain in [the repository screenshots folder](../screenshots), and v0.9r1 font-layout illustrations are in [the static preview guide](v09r1-font-qa-and-previews.md). They do not demonstrate v0.9r2 gameplay.

## Font coverage for the new wording

The two revised strings introduce three characters not previously exercised in this event asset: uppercase `D`, `O`, and `K`. This does **not** modify the font, but it does expand the required glyph coverage from 47 to **48 unique characters** in total (three additions and two previously used characters removed).

Run `python3 qa/rom_font_pixel_check_v09r2.py '/path/to/Youkaidou (Japan).gba'` with a matching clean user-owned AFUJ ROM. The script reconstructs the v0.8 font from the original and checks ink coverage for every v0.9r2 character. **This ROM-dependent font check remains pending** in the current environment. The source-free validation already performed proves encoding, cell budgets and patch containment, not actual glyph visibility or gameplay.
