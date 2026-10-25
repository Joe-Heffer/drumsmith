"""Small audio utilities that work on 16-bit PCM WAV files using only the standard library."""

import wave
from array import array
from pathlib import Path


def trim_wav(path: Path, seconds: float, fade_ms: float = 10.0) -> None:
    """Cut ``path`` to ``seconds`` long in place, with a short linear fade to avoid a click.

    Renderers without an End-of-Track option (FluidSynth) write a silent tail after the
    MIDI ends; trimming keeps the file exactly one song long so it loops cleanly.
    """
    with wave.open(str(path), "rb") as src:
        params = src.getparams()
        if params.sampwidth != 2:
            raise ValueError(f"{path}: expected 16-bit PCM, got {8 * params.sampwidth}-bit")
        keep = min(round(seconds * params.framerate), params.nframes)
        samples = array("h", src.readframes(keep))

    channels = params.nchannels
    fade_frames = min(keep, round(fade_ms / 1000 * params.framerate))
    for i in range(fade_frames):
        gain = (fade_frames - 1 - i) / fade_frames
        frame = keep - fade_frames + i
        for ch in range(channels):
            idx = frame * channels + ch
            samples[idx] = int(samples[idx] * gain)

    with wave.open(str(path), "wb") as dst:
        dst.setparams(params._replace(nframes=keep))
        dst.writeframes(samples.tobytes())
