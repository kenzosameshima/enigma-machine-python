"""Alphabet and shared Enigma constants."""

BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_ROTORS = ("I", "II", "III")
DEFAULT_RINGS = (1, 1, 1)
DEFAULT_M4_RINGS = (1, 1, 1, 1)
DEFAULT_POSITIONS = "AAA"
MOVING_ROTORS = frozenset({"I", "II", "III", "IV", "V"})
GREEK_ROTORS = frozenset({"BETA", "GAMMA"})
