"""Alphabet and shared Enigma constants."""

BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_TO_INDEX = {char: index for index, char in enumerate(BASE)}
INDEX_TO_CHAR = tuple(BASE)
DEFAULT_ROTORS = ("I", "II", "III")
DEFAULT_RINGS = (1, 1, 1)
DEFAULT_M4_RINGS = (1, 1, 1, 1)
DEFAULT_POSITIONS = "AAA"
MOVING_ROTORS = frozenset({"I", "II", "III", "IV", "V"})
GREEK_ROTORS = frozenset({"BETA", "GAMMA"})


def is_base_letter(char: str) -> bool:
    """Return whether char is one of the supported A-Z letters."""

    return char in CHAR_TO_INDEX


def letter_to_index(char: str) -> int:
    """Convert an A-Z letter to its zero-based alphabet index."""

    return CHAR_TO_INDEX[char]


def index_to_letter(index: int) -> str:
    """Convert a zero-based alphabet index to its A-Z letter."""

    return INDEX_TO_CHAR[index]
