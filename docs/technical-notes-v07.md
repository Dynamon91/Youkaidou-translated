# Youkaidou English v07 — technical notes

Four new event assets contain 186 nonempty English slots across 117 dialogue
pages and six choice menus. Source glyphs, script controls, variables and layout
were checked for the full batch. In-context verification is deliberately narrower.

| Scenario | Dialogue pages checked | Choice menus checked |
| --- | --- | --- |
| cargo road | 6 / 52 | 0 / 3 |
| cargo village | 0 / 14 | 0 / 1 |
| cargo report | 0 / 37 | 0 / 1 |
| journey village | 0 / 14 | 0 / 1 |

The six checked pages cover the driver's two help pages, Ittan-momen's two
introductions, the Ichinohe Village sign and one Healing Med pickup. All 111
other pages and six menus remain pending, with exact IDs in
`rescue_pixel_checks.json` and the translation manifests. The battle was entered
with ordinary controls; victory, the truck ride, village return, elder report,
war explanation and next departure have not been verified in context.

## Text buffer fix

Native play exposed a shared 27-cell buffer in four introductory print pairs.
Their original inter-print control is `0x4006`; regular two-line prints also
have `0x4001`. Filling the originally empty second print passed individual line
limits but truncated Ittan-momen's speech in the game. Both lines were condensed
into their first print; the second prints remain empty. The final text displays
in full, including the speaker name and cry. No control word was changed.

The manifests specify four shared-buffer limits. `script_codec.py` verifies
their original control gap and combined cell count. `check_layout_limits.py`
accepts the corrected intro and rejects the actual overflow draft:

```sh
python3 check_layout_limits.py "/path/to/Youkaidou (Japan).gba"
```

Other dialogue retains two 27-cell / 216-pixel lines; choices have an 18-cell
limit. Each player-name variable stays in its source slot with an eight-cell
budget. Branch entries, commands and variable words are retained. All 13
decoded assets fit their 64 KiB event area. The builder rebases 1154 entries
and redirects 1293 asset references. IPS application reproduces the ROM exactly.

## Translation context

The original sign identifies Ichinohe Village; later source furigana confirms
Futago Town. The driver uses a truck; the train cannot run. The elder describes
rumors of a coming war, not an already-started war. Yokai feed on the resulting
gloom. No historical date was added. Ittan-momen keeps his name and vocal cry.
Bookmarks select yokai; talismans are the battle grid. Healing Med is the concise
loot label for `かいふくやく`. Japanese source and review text are retained in
`verification/v07/translation_review.txt`.

## Verification and limits

New captures came from the final ROM with full decoded-script RAM equality
and exact final-font pixel comparisons. Draft checkpoints with stale script RAM
were excluded. Gameplay used normal controls and emulator checkpoints; no game
stats, inventory or event flags were edited. An actual 8192-byte road save passed
cancellation, completed saving, reset, Continue and overwrite cancellation. A
separate v06 backup loaded after reset; Yayoi's English dialogue confirmed that
the accepted mission survived. The road backup is before the rescue victory.

The 232 earlier dialogue-page captures, 34 choice captures and seven level-up
messages retain their provenance. Their nine event assets and both font banks
are byte-identical to v06. All archived text captures were checked again against
the final font ink; earlier gameplay was not all replayed. The full included set
now covers 238 dialogue pages, 34 choice captures and seven level-up messages.
The UI remains at 85 records: 51 with observed screen checks, 34 with static
checks only. Earlier pending branches remain pending in their own reports.

mGBA 0.10.5 ran the game at 240x160. The preview enlarges actual screenshots 3x
without smoothing. The harnesses in `verification/v07/` retain workspace paths
and require adaptation for replay. To check the canonical screenshots after
building, install Pillow, copy `rebuilt/Youkaidou_English_v07.gba` beside
`check_captures.py`, and run:

```sh
python3 check_captures.py
```

This checks archived captures; it does not replay gameplay. Later chapters,
some UI and battle labels remain Japanese. Link connectivity, later battles,
late-game saves and physical hardware remain unverified. No full-game completion
percentage is claimed. ROM files are not tracked in Git. The delivered source
ZIP was independently rebuilt to the exact release ROM and IPS bytes.
