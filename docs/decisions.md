# Decisions

A running log of engineering choices and of what was learnt from each external tool's `--help` or man page before using it.

## Tool survey (2026-10-25, milestone 1)

Host: Omarchy (Arch-based), `yay` available for the AUR.

| Tool | Found | Notes |
|---|---|---|
| `python3` | 3.14.8 (system) | The project pins 3.12; uv already had CPython 3.12.14 installed. |
| `uv` | 0.12.7 | |
| `ffmpeg`, `ffprobe` | n9.0.2 | |
| `fluidsynth` | missing | In Arch `extra` (2.6.1). GM soundfont: `soundfont-fluid`. |
| `sfizz_render` | missing | Not in the official Arch repositories. AUR or build from source (milestone 4). |
| `drumgizmo` | missing | Not in the official Arch repositories. AUR (milestone 6). |

## Engineering choices

- **Project layout.** `src/` layout, `uv` with the hatchling build backend, `ruff` for linting and formatting, `pytest`.
- **CLI with stdlib `argparse`.** Sub-commands are enough; avoids a dependency.
- **YAML via `ruamel.yaml` (from milestone 2).** It keeps line and column numbers on every node, which strict error messages need. `strictyaml` was rejected because it forbids flow mappings, which the song format's `sections` list uses. Validation will use plain dataclasses and our own checks so that every error can point at a YAML line.
- **Audio checks with `numpy` and `soundfile` (from milestone 4)**, with `ffprobe` for duration as the brief specifies.
- **Seeded RNG per instrument (milestone 3)**, derived from the song seed and the instrument name without Python's salted `hash()`, so adding a part does not reshuffle the others.
- **MIDI is type 0, one track**, PPQ 480, all notes on channel index 9. Track name, tempo and time signature sit at tick 0.
- **Note length 60 ticks**, clamped so that no note-off falls after End of Track. End of Track sits exactly at the end of the last bar so `--use-eot` renders stop cleanly.
- **Event ordering is fully deterministic:** sorted by tick, then note-offs before note-ons, then note number. Same input gives byte-identical MIDI (tested).
- **Count-in** is quarter-note side-stick clicks (GM note 37) at a fixed velocity of 90.
- **Missing dependencies** raise `MissingDependencyError`, which prints install commands for Debian/Ubuntu, Homebrew and Arch; the CLI exits with status 2 without writing anything.
- **Soundfont discovery for FluidSynth:** `--soundfont`, then `$DRUMSMITH_SOUNDFONT`, then the usual distribution paths (`/usr/share/soundfonts/FluidR3_GM.sf2` on Arch, `/usr/share/sounds/sf2/FluidR3_GM.sf2` on Debian/Ubuntu).

## FluidSynth flags (confirmed against `fluidsynth --help`, version 2.6.1)

Installed on 2026-10-25 with `pacman -S fluidsynth soundfont-fluid`, which provides `/usr/share/soundfonts/FluidR3_GM.sf2` (and `FluidR3_GS.sf2`).

Usage line: `fluidsynth [options] [soundfonts] [midifiles]`. Flags used:

| Flag | Meaning from `--help` |
|---|---|
| `-n`, `--no-midi-in` | Do not create a MIDI input driver. |
| `-i`, `--no-shell` | Do not read commands from the shell. |
| `-q`, `--quiet` | No welcome message or informational output. |
| `-F FILE`, `--fast-render` | Render the MIDI file to audio in FILE, faster than real time. |
| `-T wav`, `--audio-file-type` | File type; `-T help` lists `wav`, `flac`, `w64` and others. |
| `-O s16`, `--audio-file-format` | Sample format; `-O help` lists `s8`, `s16`, `s24`, `s32`, `float`, `double`, `u8`. |
| `-r 48000`, `--sample-rate` | Sample rate. |

Command: `fluidsynth -n -i -q -F OUT.wav -T wav -O s16 -r 48000 SOUNDFONT.sf2 IN.mid`

Findings:

- Reverb (`-R`) and chorus (`-C`) default to on. Left on for the preview.
- Master gain (`-g`) defaults to 0.2. The demo peaks at about -18.5 dBFS. Peak normalisation is planned for milestone 5, so the gain stays at its default.
- **No End-of-Track option.** The fast renderer appended about 2.4 s of silence (14.90 s for a 12.5 s song). The renderer therefore trims the WAV to the MIDI length (`mido.MidiFile.length`) with a 10 ms linear fade (`drumsmith.audio.trim_wav`). Rendering at `s16` lets that step use only the standard library `wave` module.
- In this environment, FluidSynth prints many `ALSA lib ...` messages to stderr even with `-q` and without playback. They are harmless; stderr is captured and shown only on failure.
