# drumsmith

A command-line tool that turns a short text description of a song into a humanised drum backing track to practise bass along to. A YAML song file compiles to General MIDI, which is then rendered to audio with a sampled drum kit.

**Work in progress.** Milestone 1: the MIDI writer and a FluidSynth preview of a hard-coded groove.

```sh
uv sync
uv run drumsmith demo -o out/      # write out/demo.mid
uv run drumsmith preview -o out/   # also render out/demo.wav with FluidSynth
uv run pytest
```
