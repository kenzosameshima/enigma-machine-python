"""Plugboard mapping."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import BASE


class Plugboard:
    """Bidirectional plugboard mapping."""

    def __init__(self, pairs: Sequence[tuple[str, str]] | None = None) -> None:
        self._mapping = self._build_mapping(pairs or ())

    @property
    def mapping(self) -> dict[str, str]:
        return dict(self._mapping)

    def swap(self, char: str) -> str:
        """Swap a character through the plugboard."""

        return self._mapping.get(char, char)

    def _build_mapping(
        self, pairs: Sequence[tuple[str, str]]
    ) -> dict[str, str]:
        mapping: dict[str, str] = {}
        if len(pairs) > 10:
            raise ValueError("Plugboard supports up to 10 pairs")

        for first, second in pairs:
            a = first.upper()
            b = second.upper()
            if len(a) != 1 or len(b) != 1 or a not in BASE or b not in BASE:
                raise ValueError(f"Invalid plugboard pair: {first}-{second}")
            if a == b:
                raise ValueError(f"Plugboard pair cannot repeat a letter: {a}-{b}")
            if a in mapping or b in mapping:
                raise ValueError(f"Plugboard letter already used: {a}-{b}")
            mapping[a] = b
            mapping[b] = a
        return mapping
