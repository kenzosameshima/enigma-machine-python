"""Machine mode definitions and mode-specific validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .alphabet import GREEK_ROTORS


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


class GreekRotorName(str, Enum):
    """Supported Greek rotors for M4 mode."""

    BETA = "BETA"
    GAMMA = "GAMMA"


THREE_ROTOR_REFLECTORS = frozenset({ReflectorName.B.value, ReflectorName.C.value})
M4_REFLECTORS = frozenset({ReflectorName.B_THIN.value, ReflectorName.C_THIN.value})


@dataclass(frozen=True)
class ModeSpec:
    """Sizing and reflector rules for one machine mode."""

    label: str
    rotor_count: int
    moving_rotor_count: int
    allowed_reflectors: frozenset[str]
    reflector_description: str
    requires_greek: bool


MODE_SPECS: dict[MachineModeName, ModeSpec] = {
    MachineModeName.WEHRMACHT: ModeSpec(
        label="3-rotor mode",
        rotor_count=3,
        moving_rotor_count=3,
        allowed_reflectors=THREE_ROTOR_REFLECTORS,
        reflector_description="reflector B or C",
        requires_greek=False,
    ),
    MachineModeName.NAVAL: ModeSpec(
        label="3-rotor mode",
        rotor_count=3,
        moving_rotor_count=3,
        allowed_reflectors=THREE_ROTOR_REFLECTORS,
        reflector_description="reflector B or C",
        requires_greek=False,
    ),
    MachineModeName.M4: ModeSpec(
        label="M4",
        rotor_count=4,
        moving_rotor_count=3,
        allowed_reflectors=M4_REFLECTORS,
        reflector_description="thin reflectors: B_THIN or C_THIN",
        requires_greek=True,
    ),
}


def mode_name_for(mode: MachineModeName | str) -> MachineModeName:
    """Normalize a mode name string or return an existing MachineModeName."""

    if isinstance(mode, MachineModeName):
        return mode

    try:
        return MachineModeName(str(mode).lower())
    except ValueError as exc:
        supported = ", ".join(sorted(item.value for item in MachineModeName))
        raise ValueError(
            f"Unsupported machine mode: {mode}. Supported modes: {supported}"
        ) from exc


def validate_mode(
    mode: MachineModeName,
    *,
    rotor_order: tuple[str, ...],
    ring_settings: tuple[int, ...],
    reflector_name: str,
    greek_rotor: str,
) -> None:
    """Validate rotor/ring counts and reflector choice for mode.

    Rotor position length is already guaranteed by key normalization, which
    runs before this check and sizes to the same mode's rotor_count.
    """

    spec = MODE_SPECS[mode]
    if len(rotor_order) != spec.moving_rotor_count:
        raise ValueError(f"{spec.label} requires {spec.moving_rotor_count} rotor names")
    if len(ring_settings) != spec.rotor_count:
        raise ValueError(f"{spec.label} requires {spec.rotor_count} ring settings")
    if reflector_name not in spec.allowed_reflectors:
        raise ValueError(f"{spec.label} uses {spec.reflector_description}")
    if spec.requires_greek and greek_rotor not in GREEK_ROTORS:
        raise ValueError(f"{spec.label} requires Greek rotor BETA or GAMMA")
