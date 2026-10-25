"""A hard-coded groove used to exercise the MIDI writer before the parser exists."""

from drumsmith.gm import GM_NOTES, PPQ
from drumsmith.midi import NoteEvent

BPM = 96
TIME_SIGNATURE = (4, 4)
STEPS_PER_BAR = 16
TICKS_PER_STEP = PPQ // 4  # sixteenth notes
TICKS_PER_BAR = STEPS_PER_BAR * TICKS_PER_STEP
COUNT_IN_BARS = 1
GROOVE_BARS = 4

# Fixed velocities until the humaniser arrives in milestone 3.
VELOCITIES = {"x": 80, "o": 110, "g": 40}
COUNT_IN_VELOCITY = 90

GROOVE: dict[str, str] = {
    "kick": "x...x..gx.x.....",
    "snare": "....o......g...g",
    "hihat_closed": "x.x.x.x.x.x.x.x.",
}


def demo_events() -> tuple[list[NoteEvent], int]:
    """Return the demo's note events and its total length in ticks."""
    events: list[NoteEvent] = []
    for beat in range(TIME_SIGNATURE[0] * COUNT_IN_BARS):
        events.append(NoteEvent(beat * PPQ, GM_NOTES["side_stick"], COUNT_IN_VELOCITY))
    for bar in range(COUNT_IN_BARS, COUNT_IN_BARS + GROOVE_BARS):
        for instrument, pattern in GROOVE.items():
            for step, symbol in enumerate(pattern):
                if symbol != ".":
                    tick = bar * TICKS_PER_BAR + step * TICKS_PER_STEP
                    events.append(NoteEvent(tick, GM_NOTES[instrument], VELOCITIES[symbol]))
    total_ticks = (COUNT_IN_BARS + GROOVE_BARS) * TICKS_PER_BAR
    return sorted(events), total_ticks
