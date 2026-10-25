"""Command-line interface for drumsmith."""

import argparse
import sys
from pathlib import Path

from drumsmith import __version__, demo
from drumsmith.midi import write_midi
from drumsmith.renderers import RendererError
from drumsmith.renderers.fluidsynth import FluidSynthRenderer


def _write_demo_midi(out_dir: Path) -> Path:
    events, total_ticks = demo.demo_events()
    return write_midi(
        out_dir / "demo.mid",
        events,
        bpm=demo.BPM,
        time_signature=demo.TIME_SIGNATURE,
        total_ticks=total_ticks,
        title="drumsmith demo",
    )


def cmd_demo(args: argparse.Namespace) -> int:
    path = _write_demo_midi(args.output)
    print(f"Wrote {path}")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    renderer = FluidSynthRenderer(soundfont=args.soundfont)
    try:
        renderer.check()
    except RendererError as exc:
        print(f"drumsmith: cannot preview: {exc}", file=sys.stderr)
        return 2
    midi_path = _write_demo_midi(args.output)
    wav_path = renderer.render(midi_path, midi_path.with_suffix(".wav"))
    print(f"Wrote {midi_path}\nWrote {wav_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drumsmith", description="Turn a text description of a song into a drum track."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_demo = sub.add_parser("demo", help="write the hard-coded demo groove as MIDI")
    p_demo.add_argument("-o", "--output", type=Path, default=Path("out"), help="output folder")
    p_demo.set_defaults(func=cmd_demo)

    p_preview = sub.add_parser("preview", help="render the demo groove quickly with FluidSynth")
    p_preview.add_argument("-o", "--output", type=Path, default=Path("out"), help="output folder")
    p_preview.add_argument("--soundfont", type=Path, help="General MIDI .sf2 file to use")
    p_preview.set_defaults(func=cmd_preview)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
