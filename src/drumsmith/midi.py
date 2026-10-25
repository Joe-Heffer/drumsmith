"""Write drum events to a Standard MIDI File with mido."""

from dataclasses import dataclass
from pathlib import Path

import mido

from drumsmith.gm import DRUM_CHANNEL, PPQ

NOTE_LENGTH = 60  # ticks; drum samples ignore note-off, but keep notes short and tidy


@dataclass(frozen=True, order=True)
class NoteEvent:
    """A single drum hit at an absolute tick."""

    tick: int
    note: int
    velocity: int


def build_midi(
    events: list[NoteEvent],
    *,
    bpm: float,
    time_signature: tuple[int, int],
    total_ticks: int,
    title: str = "drumsmith",
) -> mido.MidiFile:
    """Build a type 0 MIDI file whose End of Track sits exactly at ``total_ticks``.

    Note-offs are clamped so that nothing falls after the End of Track, which lets
    renderers using ``--use-eot`` stop cleanly at the end of the last bar.
    """
    timed: list[tuple[int, int, mido.Message]] = []
    for ev in events:
        if not 0 <= ev.tick < total_ticks:
            raise ValueError(f"note at tick {ev.tick} lies outside 0..{total_ticks}")
        if not 1 <= ev.velocity <= 127:
            raise ValueError(f"velocity {ev.velocity} out of range 1..127")
        off = min(ev.tick + NOTE_LENGTH, total_ticks)
        # Sort key: tick, then note-offs (0) before note-ons (1), then note number.
        timed.append(
            (
                ev.tick,
                1,
                mido.Message("note_on", channel=DRUM_CHANNEL, note=ev.note, velocity=ev.velocity),
            )
        )
        timed.append(
            (off, 0, mido.Message("note_off", channel=DRUM_CHANNEL, note=ev.note, velocity=0))
        )
    timed.sort(key=lambda t: (t[0], t[1], t[2].note))

    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name=title, time=0))
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    num, den = time_signature
    track.append(mido.MetaMessage("time_signature", numerator=num, denominator=den, time=0))

    now = 0
    for tick, _, msg in timed:
        track.append(msg.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=total_ticks - now))

    mid = mido.MidiFile(type=0, ticks_per_beat=PPQ)
    mid.tracks.append(track)
    return mid


def write_midi(
    path: Path,
    events: list[NoteEvent],
    *,
    bpm: float,
    time_signature: tuple[int, int],
    total_ticks: int,
    title: str = "drumsmith",
) -> Path:
    """Build a MIDI file (see :func:`build_midi`) and save it to ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    mid = build_midi(
        events, bpm=bpm, time_signature=time_signature, total_ticks=total_ticks, title=title
    )
    mid.save(path)
    return path
