# Youkaidou — English v05

This partial localization adds the shrine incident and the elder's explanation
of Shuten Doji and the Kidoshu. The new batch replaces 111 nonempty Japanese
fields with 125 nonempty English lines across three event assets, including
short reminders before reporting the incident. Dialogue and commands use mixed
case. HP, MP, LV, and the Journal's fixed-field `NEXT LV` retain uppercase forms.

The release also includes 85 English UI records, the complete 27-page opening,
the shared village script, and the earlier house conversations. Later scenarios,
most yokai names, character naming, the preflight notice, and some battle text
and artwork labels remain Japanese. This is a partial release.

## Play or apply the patch

`Youkaidou_English_v05.ips` applies the translation to this exact clean original:

- Header title: `YOUKAIDOU`
- Game code: `AFUJ`
- Source size: 8,388,608 bytes
- Source SHA-256: `080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06`

Apply the IPS to the clean original, not an earlier English build. The output
remains 8 MiB and retains the original GBA header. An emulator may associate
saves by ROM basename; copy and rename a backup to match the new ROM name when
necessary. A v04 save after the three initial quests was loaded successfully in
v05. Late-game save compatibility has not been checked.

## What was checked

- All 27 opening pages passed exact text-pixel comparisons after a fresh boot
  of the final ROM, followed by normal field gameplay.
- 27 of the 33 shrine pages passed exact 8x16 text-pixel comparisons, including
  both reactions to the incident. The six home, following, and rest variants
  and their home choice menu remain pending.
- All 42 elder-report pages and both selections of all three question menus
  passed. The two final question paths both reached the next story phase.
- The six translated return-to-village reminder pages have source, control,
  encoding, and width checks; they have not been encountered in the emulator.
- 52 of 57 village pages now have exact pixel checks. The newly reached offer
  from Shittara was tested with both replies through the shrine transition.
  Six choice captures cover four of the five village menus; the earlier
  menus retain only their previously recorded selections.
- 40 of 47 house pages and both selections of four of five house menus are
  checked. Seven conditional Yayoi pages and one menu remain pending.
- Seven level-up notices retain their exact 8x8 pixel checks from v04. Original
  yokai names and numerical values still come from the game. The Luck label
  has static checks; that stat did not change in the tested level-up.
- Save cancellation, a completed 8,192-byte backup after the shrine incident,
  fresh reset, Continue, and overwrite cancellation passed in v05. After
  Continue, Yayoi's report dialogue and the elder's new script loaded correctly.
  A separate v04 save retained Granny Tora's completed-quest response in v05;
  that response also passed a pixel check.
- 51 of the 85 UI records have an observed screen check. The other 34 have
  source-byte, encoding, control-sequence, and cell-budget checks. Unchanged
  UI evidence is retained from earlier versions.

The project contains **188 distinct dialogue-page captures, 22 choice captures,
and seven level-up popup captures** checked against the final ROM's fonts.
69 of the 81 pages in the three new event assets are checked. Captures from
older releases retain their provenance; their localized event streams and both
font banks are unchanged. The evidence was checked again against the final ROM.

Verification used mGBA 0.10.5 at native 240x160 resolution. Normal game controls
and emulator checkpoints reached the alternatives; no gameplay data was edited.
Dialogue retains two lines of **27 cells / 216 pixels each**. The next cell
belongs to the page indicator. Choices have an 18-cell budget. Name variables
reserve eight cells. Checked text had no missing or extra ink. Static width
checks cover the longest reserved player-name expansion as well as the default
name used in the emulator.

`validation.json`, `opening_pixel_checks.json`, `village_pixel_checks.json`,
`house_pixel_checks.json`, `story_pixel_checks.json`, `level_up_pixel_checks.json`,
and `emulator_checks.json` contain evidence and pending scope. Native captures
are under `screenshots/`. The preview enlarges two real emulator captures with
nearest-neighbor scaling. `verification/` contains the v05 capture log, save
reports, a test backup, and the emulator bridge used for this batch. The backup
is verification data, not a required game file.

Link connectivity, later battles and menus, late-game saves, and physical GBA
hardware have not been verified. No full-game completion percentage is claimed.

## Localization choices

妖怪 is yokai, 退魔師 is exorcist, 妖怪使い is yokai tamer, 手帳 is journal,
and 封印のホコラ is Seal Shrine. トクさん is Mr. Toku, ノブじい is Gramps Nobu,
トラばあさん is Granny Tora, トミさん is Tomi, やよい is Yayoi, and 長老 is the
elder. Earlier names remain Ippei, Okin, Bunmaru, and Shittara. ミロク, モンジュ,
and コンゴウ are Miroku, Monju, and Kongo; 鬼道衆 is Kidoshu; 酒呑童子 is
Shuten Doji. The elder's warning refers to the shrine **to the east**. Gold is 金.

Shuten Doji was defeated 200 years ago; his minions were sealed in the shrine.
Kongo removes the door and puts it back. The original page timing preserves the
reveal around that animation. The group's scheme creates demand for exorcisms.

Kawauso is romanized in narration, while its fixed-capacity list name remains
Japanese. The narrator stays informal and dry; Shittara remains mocking; Yayoi
is friendly and playful; the older villagers retain their familiar tone.

`translations.json` contains UI records and control bytes. The opening, village,
house, shrine, return, and elder-story manifests contain original glyph bytes,
English text, name variables, bounds, and individual verification status.
Original print, line, page, and choice commands remain intact. Existing blank
second-line slots are filled as needed; no page advances are added.

## Rebuild from the original

Python 3.8 or newer, standard library only:

```sh
python3 build_patch.py "/path/to/Youkaidou (Japan).gba" --output rebuilt
```

The builder extracts the fonts and all five event assets from the clean ROM.
It rejects other source hashes and prevents overwriting its input. No emulator
or separately extracted font is required to build.

The MSB-first LZSS streams use a 4 KiB ring initialized at 0xFEE. Literal tokens
supported by the stock decoder rebuild the scenarios. Their 454 event/branch
entry offsets are rebased and 1,276 asset references are redirected. Decoded
sizes are 9,326, 5,772, 3,922, 1,018, and 4,658 bytes, each within its 64 KiB
event-data region. Original VM commands, arguments, and name variables are retained.

The 8x8 font adds lowercase in unused slots 0x180–0x199; the 8x16 font uses
slots 0x320–0x339 while preserving the original 800 glyphs. Both conversion paths
and the small-font bootstrap are handled. The field-menu position keeps the
English labels on screen.

Level-up grammar and stat labels replace only explicitly listed references
inside the level-up renderer. Shared Japanese particles and other fixed-field
stat paths keep their original references. The builder checks this scope and
the complete sentence budgets, including dynamic fields.

Every source string, control sequence, cell budget, and scenario reference is
checked. Applying the generated IPS reproduces the ROM byte for byte. The archived v05 source was rebuilt separately and matched the release ROM and
IPS exactly. Optional `check_captures.py` uses Pillow to verify the included
screenshots against the ROM fonts; it does not replay gameplay. Hashes and
individual records are in `validation.json` and `SHA256SUMS.txt`.

ROM files are not tracked in this repository. The IPS and source reproduce the v05 translation from the specified original.
