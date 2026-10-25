"""FluidSynth backend: a quick General MIDI preview and fallback renderer."""

import os
import subprocess
from pathlib import Path

import mido

from drumsmith.audio import trim_wav
from drumsmith.renderers import (
    InstallHint,
    MissingDependencyError,
    RendererError,
    require_binary,
)

FLUIDSYNTH_HINT = InstallHint(
    debian="sudo apt install fluidsynth fluid-soundfont-gm",
    macos="brew install fluid-synth  (then download a GM soundfont and pass --soundfont)",
    arch="sudo pacman -S fluidsynth soundfont-fluid",
)

SOUNDFONT_CANDIDATES = (
    Path("/usr/share/soundfonts/FluidR3_GM.sf2"),  # Arch soundfont-fluid
    Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"),  # Debian/Ubuntu fluid-soundfont-gm
    Path("/usr/share/soundfonts/default.sf2"),
    Path("/opt/homebrew/share/soundfonts/default.sf2"),
    Path("/usr/local/share/soundfonts/default.sf2"),
)


def find_soundfont(explicit: Path | None = None) -> Path:
    """Locate a General MIDI soundfont, preferring an explicit path or $DRUMSMITH_SOUNDFONT."""
    env = os.environ.get("DRUMSMITH_SOUNDFONT")
    candidates = [p for p in (explicit, Path(env) if env else None) if p is not None]
    if candidates:
        if not candidates[0].is_file():
            raise RendererError(f"soundfont not found: {candidates[0]}")
        return candidates[0]
    for path in SOUNDFONT_CANDIDATES:
        if path.is_file():
            return path
    raise MissingDependencyError("A General MIDI soundfont (FluidR3_GM.sf2)", FLUIDSYNTH_HINT)


class FluidSynthRenderer:
    """Render with the ``fluidsynth`` command-line synthesiser."""

    name = "fluidsynth"

    def __init__(self, soundfont: Path | None = None, sample_rate: int = 48000) -> None:
        self._soundfont = soundfont
        self.sample_rate = sample_rate

    def check(self) -> None:
        require_binary("fluidsynth", FLUIDSYNTH_HINT)
        find_soundfont(self._soundfont)

    def command(self, midi_path: Path, wav_path: Path) -> list[str]:
        """Build the fluidsynth command line (flags recorded in docs/decisions.md)."""
        binary = require_binary("fluidsynth", FLUIDSYNTH_HINT)
        return [
            binary,
            "-n",  # no MIDI input driver
            "-i",  # no interactive shell
            "-q",  # quiet
            "-F",
            str(wav_path),  # fast-render to this file
            "-T",
            "wav",
            "-O",
            "s16",  # 16-bit PCM so trim_wav can use the standard library
            "-r",
            str(self.sample_rate),
            str(find_soundfont(self._soundfont)),
            str(midi_path),
        ]

    def render(self, midi_path: Path, wav_path: Path) -> Path:
        wav_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            self.command(midi_path, wav_path), capture_output=True, text=True, check=False
        )
        if result.returncode != 0 or not wav_path.is_file():
            raise RendererError(
                f"fluidsynth failed (exit {result.returncode}):\n{result.stderr.strip()}"
            )
        # FluidSynth has no End-of-Track option and appends a silent tail; cut it off.
        trim_wav(wav_path, mido.MidiFile(midi_path).length)
        return wav_path
