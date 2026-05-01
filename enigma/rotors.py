"""Rotor definitions and rotor behavior."""

from __future__ import annotations

from dataclasses import dataclass

from .alphabet import BASE


@dataclass(frozen=True)
class RotorSpec:
    """Immutable rotor definition."""

    name: str
    wiring: str
    notch: str


@dataclass
class RotorState:
    """Mutable rotor state."""

    ring: int
    position: int


class Rotor:
    """Rotor behavior backed by immutable spec and mutable state."""

    def __init__(
        self,
        spec: RotorSpec | str,
        state: RotorState | None = None,
        can_step: bool = True,
        ring_setting: int = 1,
        position: str = "A",
    ) -> None:
        if isinstance(spec, str):
            from .data import ROTOR_SPECS

            spec = ROTOR_SPECS[spec]

        self.spec = spec
        self.name = self.spec.name
        self.state = state or RotorState(
            ring=ring_setting - 1,
            position=BASE.index(position),
        )
        self.can_step = can_step
        self.wiring = [BASE.index(char) for char in self.spec.wiring]
        self.inverse_wiring = [0] * 26
        for index, mapped in enumerate(self.wiring):
            self.inverse_wiring[mapped] = index
        self.notches = [BASE.index(char) for char in self.spec.notch]

    @property
    def ring(self) -> int:
        return self.state.ring

    @property
    def position(self) -> int:
        return self.state.position

    def at_notch(self) -> bool:
        """Return whether this rotor is currently at its turnover notch."""

        return (self.position + self.ring) % 26 in self.notches

    def get_position_letter(self) -> str:
        """Return the current window letter."""

        return BASE[self.position]

    def step(self) -> None:
        """Advance the rotor if it is allowed to move."""

        if self.can_step:
            self.state.position = (self.position + 1) % 26

    def encode_forward(self, index: int) -> int:
        """Encode right-to-left through the rotor."""

        shifted = (index + self.position - self.ring) % 26
        wired = self.wiring[shifted]
        return (wired - self.position + self.ring) % 26

    def encode_backward(self, index: int) -> int:
        """Encode left-to-right through the inverse rotor wiring."""

        shifted = (index + self.position - self.ring) % 26
        wired = self.inverse_wiring[shifted]
        return (wired - self.position + self.ring) % 26
