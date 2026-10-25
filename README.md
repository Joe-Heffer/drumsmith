# drumsmith

A command-line tool that turns a short text description of a song into a humanised drum backing track to practise bass along to. A YAML song file compiles to General MIDI, which is then rendered to audio with a sampled drum kit.

**Work in progress.** Milestone 1 of the [roadmap](docs/roadmap.md) is done: the MIDI writer and a FluidSynth preview of a hard-coded groove.

```sh
uv sync
uv run drumsmith demo -o out/      # write out/demo.mid
uv run drumsmith preview -o out/   # also render out/demo.wav with FluidSynth
```

## Development

```sh
uv sync
uv run pre-commit install          # run ruff and mypy on every commit
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest
```

The preview tests need `fluidsynth`, a General MIDI soundfont and `ffmpeg`; they are skipped when these are missing. Engineering choices are logged in [docs/decisions.md](docs/decisions.md).

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:` …). [release-please](https://github.com/googleapis/release-please) uses them to open release PRs that bump the version and update `CHANGELOG.md`.

## Licence

The code is released under the [MIT licence](LICENSE). drumsmith ships no samples; the licences of the drum kits it downloads are listed in [LICENSES.md](LICENSES.md).
