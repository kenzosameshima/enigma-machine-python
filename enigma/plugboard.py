"""Plugboard mapping."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import is_base_letter


class Plugboard:
    """Bidirectional plugboard mapping."""

    def __init__(self, pairs: Sequence[tuple[str, str]] | None = None) -> None:
        self._mapping = self._build_mapping(pairs or ())

    @property
    def mapping(self) -> dict[str, str]:
        """Return a copy of the normalized bidirectional mapping."""

        return dict(self._mapping)

    def swap(self, char: str) -> str:
        """Swap a character through the plugboard."""

        return self._mapping.get(char, char)

    def _build_mapping(self, pairs: Sequence[tuple[str, str]]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        if len(pairs) > 10:
            raise ValueError("Plugboard supports up to 10 pairs")

        for pair in pairs:
            a, b = _normalize_pair(pair)
            if a == b:
                raise ValueError(f"Plugboard pair cannot repeat a letter: {a}-{b}")
            if a in mapping or b in mapping:
                raise ValueError(f"Plugboard letter already used: {a}-{b}")
            mapping[a] = b
            mapping[b] = a
        return mapping


def _normalize_pair(pair: object) -> tuple[str, str]:
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        raise ValueError("Plugboard pair must contain exactly two letters")

    first, second = pair
    if not isinstance(first, str) or not isinstance(second, str):
        raise ValueError("Plugboard pair values must be letters")

    a = first.upper()
    b = second.upper()
    if len(a) != 1 or len(b) != 1 or not is_base_letter(a) or not is_base_letter(b):
        raise ValueError(f"Invalid plugboard pair: {first}-{second}")
    return a, b
