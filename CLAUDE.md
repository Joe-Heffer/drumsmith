# drumsmith

CLI that compiles a YAML song description into General MIDI drums, then renders audio with a sampled kit. Python 3.12, `uv`, `src/` layout.

## Commands

```sh
uv sync
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest
uv run drumsmith demo -o out/
uv run drumsmith preview -o out/   # needs fluidsynth + a GM soundfont
```

## Layout

- `src/drumsmith/gm.py`: GM percussion note numbers, PPQ, drum channel.
- `src/drumsmith/midi.py`: `NoteEvent` and the type 0 MIDI writer.
- `src/drumsmith/demo.py`: hard-coded groove used until the parser exists.
- `src/drumsmith/renderers/`: the `Renderer` protocol, `MissingDependencyError`, and backends (FluidSynth so far).
- `src/drumsmith/audio.py`: stdlib WAV utilities.
- `docs/roadmap.md`: milestones. `docs/decisions.md`: engineering choices and tool findings.

## Rules

- Work one milestone at a time (see `docs/roadmap.md`). Stop after each, run the checks and report briefly before continuing. Tick it off in the roadmap.
- MIDI output must be deterministic: the same input gives byte-identical files.
- Never commit samples, soundfonts, kits or rendered audio (see `.gitignore`). List every supported kit's licence in `LICENSES.md`.
- A missing external tool raises `MissingDependencyError` with Debian/Ubuntu, Homebrew and Arch install hints; the CLI exits 2 without writing anything.
- Before using an external tool, read its `--help` or man page and record the flags and findings in `docs/decisions.md`. Log any new engineering choice there too.
- mypy runs in strict mode; keep everything annotated.
- Commit messages use Conventional Commits; release-please drives versioning, so don't hand-edit the version or `CHANGELOG.md`.
