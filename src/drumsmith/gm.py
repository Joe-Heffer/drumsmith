"""General MIDI percussion constants for the logical instruments drumsmith supports."""

PPQ = 480
DRUM_CHANNEL = 9  # MIDI channel 10, zero-indexed

GM_NOTES: dict[str, int] = {
    "kick": 36,
    "side_stick": 37,
    "snare": 38,
    "hihat_closed": 42,
    "hihat_pedal": 44,
    "tom_low": 45,
    "hihat_open": 46,
    "tom_mid": 47,
    "crash": 49,
    "tom_high": 50,
    "ride": 51,
    "ride_bell": 53,
}
