# Youkaidou English v08 — technical notes

v08 verifies the delivery rescue and subsequent quest, adds one inventory name,
and corrects two elder lines. The four-event batch still contains 186 nonempty
English text slots. Its actual layout contains 116 dialogue screens and six menus.

| Scenario | Dialogue pages checked | Menus checked with both selections |
| --- | --- | --- |
| cargo road | 46 / 52 | 3 / 3 |
| cargo village | 14 / 14 | 1 / 1 |
| cargo report | 32 / 36 | 1 / 1 |
| journey village | 14 / 14 | 1 / 1 |

The 106 checked screens include the rescue/ride home, both praise replies, the
bumpy-road joke, accepting/refusing the driver's request, both elder replies,
and all outdoor/home conversations before and after accepting the next quest.
The ten pending pages are road 6–7 (the other medicine chest), road 49–52
(full inventory), report 15 (Gramps Nobu), and report 20–22 (conditional Yayoi).
Their exact record IDs are listed in `rescue_pixel_checks.json`.

## Dialogue corrections and screen layout

The elder's rebuttal now says **No**, matching `いや`, and his explanation uses
the correct perfect tense: “I think they've fed on it and grown savage.” His
warning still describes rumors of an impending war. No historical date was added.

The elder's final order is one screen with two lines. A portrait-expression
command intervenes between its print commands. v07 mistakenly counted these as
two pages; the corrected 116-page total reflects the actual layout. The original
commands were preserved. The old v07 loot caption was also corrected: its checked
chest held 5 gold. A medicine chest is now independently checked in v08.

Dialogue keeps 27 cells / 216 pixels per line, with an eight-cell player-name
budget in its original slot. Choices have an 18-cell limit. The four introductory
NPC pairs retain the shared 27-cell buffer check added in v07. Neither tags,
variable words nor VM commands were changed.

## Inventory name and item safety

`HP Med` is the six-cell inventory abbreviation of Healing Med. Its source name
is embedded in an item record, so a separate string relocation could detach the
effect data. The replacement uses exactly the original 14-byte span, including
the control terminator and NUL. All 58 references to the item and its following
effect/price data remain byte-identical. Normal use was checked: the test yokai
went from 37 HP to 65 HP, recovering 28 HP up to its maximum. Shop transactions
and other item types have not been tested in this update.

`check_item_layout.py` accepts the exact-size name and rejects shorter/longer
names without changing the item data. `check_layout_limits.py` retains the actual
NPC overflow regression. Both use the required clean original ROM:

```sh
python3 check_item_layout.py "/path/to/Youkaidou (Japan).gba"
python3 check_layout_limits.py "/path/to/Youkaidou (Japan).gba"
```

## Verification and limits

mGBA 0.10.5 ran the game at 240x160. Normal D-pad/A inputs, item use and emulator
checkpoint branches reached the recorded paths; no stats, inventory or quest
flags were edited. The rescue battle was won. Canonical checkpoints were resumed
in the final ROM, their entire decoded event matched the final asset, and both
lines or selected choice rows matched the final font ink exactly.

An actual 8192-byte save after the elder's assignment passed cancellation,
completed saving, reset, Continue and overwrite cancellation. The continued
game loaded the exact next-quest village script. A separate v07 road save loaded
after reset and retained its earlier delivery mission, with the driver's English
help page checked again. The optional v08 backup is included in the separate v08 project ZIP.
Harnesses in this repository retain original workspace paths and need adaptation
for replay.

The earlier 232-page set and its 34 choice captures retain their provenance;
their event assets and both font banks are unchanged. Six v07 rescue pages are
included in the new canonical batch rather than counted twice. The complete set
now covers 338 dialogue pages, 46 choice captures, seven level-up messages and
five item checks. The UI has 86 localized records: 53 with observed checks and
33 with static checks only. Earlier pending branches remain pending.

The builder rebuilds 13 event assets, rebases 1154 entries and redirects 1293
event-asset references. Each decoded asset fits its 64 KiB event area. IPS
application reproduces the ROM exactly. The delivered source ZIP was rebuilt
independently to the exact release ROM and IPS bytes, and its CRC check passed.

To recheck the canonical screenshots, install Pillow, copy the rebuilt
`Youkaidou_English_v08.gba` beside `check_captures.py`, and run:

```sh
python3 check_captures.py
```

This checks archived pixels; it does not replay the game. Later chapters,
post-warning house dialogue, some UI/battle labels and most yokai names remain
Japanese. Link connectivity, later battles, late-game saves and physical hardware
remain unverified. No full-game completion percentage is claimed. ROM files are
not tracked in Git. The preview scales actual captures 3x without smoothing.
