"""Configuration model for Enigma machines."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .alphabet import (
    DEFAULT_POSITIONS,
    DEFAULT_RINGS,
    DEFAULT_ROTORS,
    GREEK_ROTORS,
    ascii_upper,
    is_base_letter,
    validate_moving_rotor_names,
)
from .data import REFLECTORS
from .modes import (
    MODE_SPECS,
    MachineModeName,
    ReflectorName,
    mode_name_for,
    validate_mode,
)
from .plugboard import Plugboard


def _normalize_key_positions(key: str, rotor_count: int) -> str:
    if not isinstance(key, str):
        raise ValueError("Key must be text containing rotor position letters")
    normalized = ascii_upper(key.strip())
    if len(normalized) != rotor_count or not all(
        is_base_letter(char) for char in normalized
    ):
        raise ValueError(f"Key must contain exactly {rotor_count} letters")
    return normalized


def _normalize_rotor_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("Rotor names must be text")
    return name.strip().upper()


def _normalize_reflector_name(name: str) -> str:
    # ReflectorName is itself a str subclass, so an enum member already
    # normalizes correctly through the plain-string path below.
    if not isinstance(name, str):
        raise ValueError("Reflector name must be text")
    return name.strip().upper()


def _normalize_greek_rotor_name(name: str) -> str:
    # GreekRotorName is itself a str subclass; see _normalize_reflector_name.
    if not isinstance(name, str):
        raise ValueError("Greek rotor must be text")
    return name.strip().upper()


def _validate_moving_rotors(rotor_order: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(_normalize_rotor_name(name) for name in rotor_order)
    validate_moving_rotor_names(normalized)
    return normalized


def _validate_ring_settings(ring_settings: Sequence[int]) -> tuple[int, ...]:
    try:
        normalized = tuple(int(setting) for setting in ring_settings)
    except (TypeError, ValueError) as exc:
        raise ValueError("Ring settings must be integers between 1 and 26") from exc
    if any(setting < 1 or setting > 26 for setting in normalized):
        raise ValueError("Ring settings must be between 1 and 26")
    return normalized


def _validate_reflector_and_greek(config: EnigmaConfig) -> None:
    """Validate reflector and Greek rotor identity, regardless of mode.

    The Greek rotor is checked unconditionally, even in three-rotor mode
    where it goes unused, so there is one rule for what counts as a valid
    Greek rotor rather than a silently-ignored field.
    """

    if config.reflector_name not in REFLECTORS:
        raise ValueError(f"Unknown reflector: {config.reflector_name}")
    if config.greek_rotor_name not in GREEK_ROTORS:
        raise ValueError(f"Unknown Greek rotor: {config.greek_rotor_name}")


@dataclass(frozen=True)
class EnigmaConfig:
    """Complete machine settings: rotors, rings, key, reflector, plugboard.

    Validated once, in __post_init__, on every construction path. Defaults
    describe a default three-rotor machine; they are not adjusted for mode,
    so e.g. mode="m4" without matching ring_settings/key raises a ValueError
    just as any other wrong count would.
    """

    rotor_order: tuple[str, ...] = DEFAULT_ROTORS
    ring_settings: tuple[int, ...] = DEFAULT_RINGS
    key: str = DEFAULT_POSITIONS
    reflector_name: str = ReflectorName.B.value
    plugboard_pairs: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    greek_rotor_name: str = "BETA"
    mode: MachineModeName = MachineModeName.WEHRMACHT

    def __post_init__(self) -> None:
        """Validate and normalize fields identically for every construction path."""

        mode = mode_name_for(self.mode)

        object.__setattr__(self, "mode", mode)
        object.__setattr__(
            self, "rotor_order", _validate_moving_rotors(self.rotor_order)
        )
        object.__setattr__(
            self, "ring_settings", _validate_ring_settings(self.ring_settings)
        )
        object.__setattr__(
            self,
            "key",
            _normalize_key_positions(self.key, MODE_SPECS[mode].rotor_count),
        )
        object.__setattr__(
            self, "reflector_name", _normalize_reflector_name(self.reflector_name)
        )
        object.__setattr__(
            self,
            "greek_rotor_name",
            _normalize_greek_rotor_name(self.greek_rotor_name),
        )
        object.__setattr__(
            self,
            "plugboard_pairs",
            tuple(tuple(pair) for pair in self.plugboard_pairs),
        )

        _validate_reflector_and_greek(self)
        validate_mode(
            mode,
            rotor_order=self.rotor_order,
            ring_settings=self.ring_settings,
            reflector_name=self.reflector_name,
        )
        Plugboard(self.plugboard_pairs)
