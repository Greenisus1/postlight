# Postlight

A fullscreen, offline sticky-note board for Raspberry Pi and Linux terminals. Pin colored notes on a board, drag them around with the arrow keys, and save the whole board to a FILENAME.postlight file you can reopen later. No cloud, no account - just a local file.

## Run

```
python3 postlight.py                 # new board
python3 postlight.py board.postlight # open a saved board
```

Python 3 with curses. No other dependencies, no network, no install.

## Controls

**View mode**

- **Enter** - new yellow note, then just type; **Enter** saves it
- **Arrow keys** - pan the board
- **Tab** - switch selected note
- **W A S D** - move the selected note
- **E** - edit the selected note's text
- **C** - cycle color (extra: yellow, pink, green, blue, orange)
- **X** - delete the selected note
- **Q** - save and quit

**Autosave:** the board saves atomically after every change and on exit - a power cut loses nothing.

## The .postlight file

Boards save as UTF-8 JSON with a `Postlight` format marker. Invalid or foreign files are rejected on open, and saves refuse to write through symlinks.

## Install from the Pi App Store

Search for `postlight` in the office-tools category, or use `app-store.sh` directly:

```
bash app-store.sh INSTALL
bash app-store.sh StAtUs
bash app-store.sh RUN
```

## Tests

```
python3 test_postlight.py   # 14 unit tests
python3 test_terminal.py    # real PTY create/edit/move/save/restore check
```

## Scope

Local unit and PTY tests cover note add/edit/delete/move with board bounds, color cycling, title caps, save suffix handling, atomic autosave (no temp files left), save/load roundtrip, rejection of non-Postlight files, note cleanup on load, symlink refusal, board format, Enter-create-type-Enter-save flow, arrow panning, WASD note moves, default filename, resizing and clean terminal exit. Before publication, all 17 unit tests and the PTY create/type/save/pan/autosave/resize checks passed on a real aarch64 Raspberry Pi.

MIT licensed (Greenisus1).
