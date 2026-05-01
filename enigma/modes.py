"""Machine mode strategies and mode-specific validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import EnigmaConfig


class MachineModeName(str, Enum):
    """Supported Enigma machine modes."""

    WEHRMACHT = "wehrmacht"
    NAVAL = "naval"
    M4 = "m4"


class ReflectorName(str, Enum):
    """Supported reflector names."""

    B = "B"
    C = "C"
    B_THIN = "B_THIN"
    C_THIN = "C_THIN"


THREE_ROTOR_REFLECTORS = frozenset({ReflectorName.B.value, ReflectorName.C.value})
M4_REFLECTORS = frozenset(
    {ReflectorName.B_THIN.value, ReflectorName.C_THIN.value}
)


class MachineMode(ABC):
    """Strategy for mode-specific validation and sizing rules."""

    name: MachineModeName

    @abstractmethod
    def validate(self, config: "EnigmaConfig") -> None:
        """Validate mode-specific configuration."""

    @abstractmethod
    def rotor_count(self) -> int:
        """Return the number of positions displayed by this mode."""

    @abstractmethod
    def moving_rotor_count(self) -> int:
        """Return the number of stepping rotors."""


class ThreeRotorMode(MachineMode):
    """Strategy for Wehrmacht/Naval three-rotor machines."""

    def __init__(self, name: MachineModeName = MachineModeName.WEHRMACHT) -> None:
        self.name = name

    def validate(self, config: "EnigmaConfig") -> None:
        if len(config.rotor_order) != self.moving_rotor_count():
            raise ValueError("3-rotor mode requires 3 rotor names")
        if len(config.ring_settings) != self.rotor_count():
            raise ValueError("3-rotor mode requires 3 ring settings")
        if len(config.positions) != self.rotor_count():
            raise ValueError("3-rotor mode requires 3 rotor positions")
        if config.reflector_name not in THREE_ROTOR_REFLECTORS:
            raise ValueError("3-rotor mode uses reflector B or C")

    def rotor_count(self) -> int:
        return 3

    def moving_rotor_count(self) -> int:
        return 3


class M4Mode(MachineMode):
    """Strategy for Naval M4 machines."""

    name = MachineModeName.M4

    def validate(self, config: "EnigmaConfig") -> None:
        from .alphabet import GREEK_ROTORS

        if len(config.rotor_order) != self.moving_rotor_count():
            raise ValueError("M4 requires 3 moving rotor names")
        if len(config.ring_settings) != self.rotor_count():
            raise ValueError("M4 requires 4 ring settings")
        if len(config.positions) != self.rotor_count():
            raise ValueError("M4 requires 4 rotor positions")
        if config.reflector_name not in M4_REFLECTORS:
            raise ValueError("M4 uses thin reflectors: B_THIN or C_THIN")
        if config.greek_rotor not in GREEK_ROTORS:
            raise ValueError("M4 requires Greek rotor BETA or GAMMA")

    def rotor_count(self) -> int:
        return 4

    def moving_rotor_count(self) -> int:
        return 3


def mode_strategy_for(mode: MachineModeName | str | MachineMode) -> MachineMode:
    """Create a mode strategy from a mode name or return an existing strategy."""

    if isinstance(mode, MachineMode):
        return mode

    if isinstance(mode, MachineModeName):
        normalized = mode
    else:
        normalized = MachineModeName(str(mode).lower())

    strategies = {
        MachineModeName.WEHRMACHT: ThreeRotorMode(MachineModeName.WEHRMACHT),
        MachineModeName.NAVAL: ThreeRotorMode(MachineModeName.NAVAL),
        MachineModeName.M4: M4Mode(),
    }
    return strategies[normalized]
