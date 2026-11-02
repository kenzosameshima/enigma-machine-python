"""Alphabet and shared Enigma constants."""

from collections.abc import Sequence

BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_TO_INDEX = {char: index for index, char in enumerate(BASE)}
INDEX_TO_CHAR = tuple(BASE)
DEFAULT_ROTORS = ("I", "II", "III")
DEFAULT_RINGS = (1, 1, 1)
DEFAULT_M4_RINGS = (1, 1, 1, 1)
DEFAULT_POSITIONS = "AAA"
MOVING_ROTORS = frozenset({"I", "II", "III", "IV", "V"})
GREEK_ROTORS = frozenset({"BETA", "GAMMA"})


def ascii_upper(text: str) -> str:
    """Uppercase ASCII a-z, preserving every other character exactly."""

    return "".join(char.upper() if "a" <= char <= "z" else char for char in text)


def is_base_letter(char: str) -> bool:
    """Return whether char is one of the supported A-Z letters."""

    return char in CHAR_TO_INDEX


def validate_moving_rotor_names(names: Sequence[str]) -> None:
    """Shared rule for which rotor names are valid moving rotors."""

    if any(name not in MOVING_ROTORS for name in names):
        raise ValueError("Moving rotors must be selected from I, II, III, IV, V")
    if len(set(names)) != len(names):
        raise ValueError("Moving rotors must be unique")


def letter_to_index(char: str) -> int:
    """Convert an A-Z letter to its zero-based alphabet index."""

    return CHAR_TO_INDEX[char]


def index_to_letter(index: int) -> str:
    """Convert a zero-based alphabet index to its A-Z letter."""

    return INDEX_TO_CHAR[index]
