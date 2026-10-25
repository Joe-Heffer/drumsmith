"""End-to-end FluidSynth preview checks. Skipped when FluidSynth or ffmpeg is missing."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from drumsmith import demo
from drumsmith.cli import main
from drumsmith.renderers.fluidsynth import find_soundfont


def _have_preview_tools() -> bool:
    if not all(shutil.which(t) for t in ("fluidsynth", "ffprobe", "ffmpeg")):
        return False
    try:
        find_soundfont()
    except Exception:
        return False
    return True


pytestmark = pytest.mark.skipif(not _have_preview_tools(), reason="FluidSynth/ffmpeg not installed")


@pytest.fixture(scope="module")
def demo_wav(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("preview")
    assert main(["preview", "-o", str(out)]) == 0
    return out / "demo.wav"


def test_duration_matches_midi(demo_wav: Path) -> None:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(demo_wav),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    bars = demo.COUNT_IN_BARS + demo.GROOVE_BARS
    expected = bars * demo.TIME_SIGNATURE[0] * 60 / demo.BPM
    assert abs(float(result.stdout) - expected) <= 0.050


def test_not_silent_and_below_full_scale(demo_wav: Path) -> None:
    result = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(demo_wav), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    max_db = float(re.search(r"max_volume: (-?[\d.]+|-inf) dB", result.stderr).group(1))
    assert -60.0 < max_db < 0.0
