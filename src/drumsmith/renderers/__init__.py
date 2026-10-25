"""Audio renderers that turn a drumsmith MIDI file into a WAV file."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class RendererError(RuntimeError):
    """A renderer could not produce audio."""


@dataclass(frozen=True)
class InstallHint:
    """How to install a missing dependency on each supported platform."""

    debian: str
    macos: str
    arch: str


class MissingDependencyError(RendererError):
    """A binary or data file a renderer needs is not available."""

    def __init__(self, what: str, hint: InstallHint) -> None:
        self.what = what
        self.hint = hint
        super().__init__(
            f"{what} is not installed.\n"
            f"  Debian/Ubuntu:    {hint.debian}\n"
            f"  macOS (Homebrew): {hint.macos}\n"
            f"  Arch:             {hint.arch}"
        )


def require_binary(name: str, hint: InstallHint) -> str:
    """Return the full path to ``name`` or raise :class:`MissingDependencyError`."""
    path = shutil.which(name)
    if path is None:
        raise MissingDependencyError(f"'{name}'", hint)
    return path


class Renderer(Protocol):
    """Renders a MIDI file to a WAV file."""

    name: str

    def check(self) -> None:
        """Raise :class:`MissingDependencyError` if the backend cannot run."""

    def render(self, midi_path: Path, wav_path: Path) -> Path:
        """Render ``midi_path`` to ``wav_path`` and return the WAV path."""
