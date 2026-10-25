"""Verify the MIDI writer using the hard-coded demo groove."""

from pathlib import Path

import mido
import pytest

from drumsmith import demo
from drumsmith.cli import main
from drumsmith.gm import DRUM_CHANNEL, GM_NOTES, PPQ
from drumsmith.midi import NoteEvent, build_midi


@pytest.fixture
def demo_midi(tmp_path: Path) -> mido.MidiFile:
    assert main(["demo", "-o", str(tmp_path)]) == 0
    return mido.MidiFile(tmp_path / "demo.mid")


def absolute(track: mido.MidiTrack) -> list[tuple[int, mido.Message]]:
    now, out = 0, []
    for msg in track:
        now += msg.time
        out.append((now, msg))
    return out


def test_header(demo_midi: mido.MidiFile) -> None:
    assert demo_midi.type == 0
    assert demo_midi.ticks_per_beat == PPQ == 480
    assert len(demo_midi.tracks) == 1


def test_tempo_and_time_signature_at_start(demo_midi: mido.MidiFile) -> None:
    metas = [(t, m) for t, m in absolute(demo_midi.tracks[0]) if m.is_meta]
    tempos = [(t, m) for t, m in metas if m.type == "set_tempo"]
    sigs = [(t, m) for t, m in metas if m.type == "time_signature"]
    assert tempos == [(0, tempos[0][1])] and tempos[0][1].tempo == 625_000  # 96 bpm
    assert len(sigs) == 1 and sigs[0][0] == 0
    assert (sigs[0][1].numerator, sigs[0][1].denominator) == (4, 4)


def test_end_of_track_exactly_at_last_bar(demo_midi: mido.MidiFile) -> None:
    events = absolute(demo_midi.tracks[0])
    eot_tick, eot = events[-1]
    assert eot.type == "end_of_track"
    assert eot_tick == (demo.COUNT_IN_BARS + demo.GROOVE_BARS) * 4 * PPQ
    assert all(t <= eot_tick for t, _ in events)


def test_all_notes_on_drum_channel(demo_midi: mido.MidiFile) -> None:
    notes = [m for m in demo_midi.tracks[0] if m.type in ("note_on", "note_off")]
    assert notes and all(m.channel == DRUM_CHANNEL for m in notes)


def test_note_counts_per_bar(demo_midi: mido.MidiFile) -> None:
    bar_ticks = 4 * PPQ
    counts: dict[tuple[int, int], int] = {}
    for tick, msg in absolute(demo_midi.tracks[0]):
        if msg.type == "note_on" and msg.velocity > 0:
            key = (tick // bar_ticks, msg.note)
            counts[key] = counts.get(key, 0) + 1

    assert counts[(0, GM_NOTES["side_stick"])] == 4
    assert not any(bar == 0 and note != GM_NOTES["side_stick"] for bar, note in counts)
    for bar in range(1, 1 + demo.GROOVE_BARS):
        for instrument, pattern in demo.GROOVE.items():
            expected = sum(1 for s in pattern if s != ".")
            assert counts[(bar, GM_NOTES[instrument])] == expected, (bar, instrument)


def test_velocities_follow_symbols(demo_midi: mido.MidiFile) -> None:
    velocities = {m.velocity for m in demo_midi.tracks[0] if m.type == "note_on"}
    assert velocities == {40, 80, 90, 110}


def test_output_is_byte_identical(tmp_path: Path) -> None:
    main(["demo", "-o", str(tmp_path / "a")])
    main(["demo", "-o", str(tmp_path / "b")])
    assert (tmp_path / "a/demo.mid").read_bytes() == (tmp_path / "b/demo.mid").read_bytes()


def test_note_off_clamped_to_end_of_track() -> None:
    mid = build_midi([NoteEvent(1910, 36, 100)], bpm=120, time_signature=(4, 4), total_ticks=1920)
    events = absolute(mid.tracks[0])
    assert [t for t, m in events if m.type == "note_off"] == [1920]
    assert events[-1] == (1920, events[-1][1]) and events[-1][1].type == "end_of_track"


@pytest.mark.parametrize(
    "event", [NoteEvent(1920, 36, 100), NoteEvent(-1, 36, 100), NoteEvent(0, 36, 0)]
)
def test_rejects_out_of_range_events(event: NoteEvent) -> None:
    with pytest.raises(ValueError):
        build_midi([event], bpm=120, time_signature=(4, 4), total_ticks=1920)
