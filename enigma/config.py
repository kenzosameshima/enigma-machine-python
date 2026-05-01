"""Configuration model and builder for Enigma machines."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .alphabet import (
    BASE,
    DEFAULT_M4_RINGS,
    DEFAULT_POSITIONS,
    DEFAULT_RINGS,
    DEFAULT_ROTORS,
    MOVING_ROTORS,
)
from .data import REFLECTORS, ROTOR_SPECS
from .modes import (
    MachineMode,
    MachineModeName,
    ReflectorName,
    ThreeRotorMode,
    mode_strategy_for,
)
from .plugboard import Plugboard


def parse_key_positions(key: str, rotor_count: int) -> str:
    """Keep valid letters and pad missing positions with A."""

    normalized = "".join(ch for ch in key.upper() if ch in BASE)
    if len(normalized) < rotor_count:
        normalized = (normalized + ("A" * rotor_count))[:rotor_count]
    return normalized[:rotor_count]


def _normalize_rotor_name(name: str) -> str:
    return name.strip().upper()


def _normalize_reflector_name(name: str | ReflectorName) -> str:
    if isinstance(name, ReflectorName):
        return name.value
    return name.strip().upper()


def _validate_moving_rotors(rotor_order: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(_normalize_rotor_name(name) for name in rotor_order)
    if any(name not in MOVING_ROTORS for name in normalized):
        raise ValueError("Moving rotors must be selected from I, II, III, IV, V")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Moving rotors must be unique")
    return normalized


def _validate_ring_settings(ring_settings: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(int(setting) for setting in ring_settings)
    if any(setting < 1 or setting > 26 for setting in normalized):
        raise ValueError("Ring settings must be between 1 and 26")
    return normalized


@dataclass(frozen=True)
class EnigmaConfig:
    """Complete machine configuration."""

    text: str
    mode: MachineModeName
    rotor_order: tuple[str, ...]
    ring_settings: tuple[int, ...]
    positions: str
    reflector_name: str
    plugboard_pairs: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    greek_rotor: str = "BETA"
    mode_strategy: MachineMode = field(default_factory=ThreeRotorMode)


class EnigmaConfigBuilder:
    """Fluent builder that centralizes Enigma configuration validation."""

    def __init__(self) -> None:
        self._text = ""
        self._mode: MachineModeName | str | MachineMode = MachineModeName.WEHRMACHT
        self._rotor_order: Sequence[str] = DEFAULT_ROTORS
        self._ring_settings: Sequence[int] | None = None
        self._key = DEFAULT_POSITIONS
        self._reflector_name: str | ReflectorName = ReflectorName.B
        self._plugboard_pairs: Sequence[tuple[str, str]] = ()
        self._greek_rotor = "BETA"

    def text(self, value: str) -> "EnigmaConfigBuilder":
        self._text = value
        return self

    def mode(self, value: MachineModeName | str | MachineMode) -> "EnigmaConfigBuilder":
        self._mode = value
        return self

    def rotors(self, *rotor_order: str | Sequence[str]) -> "EnigmaConfigBuilder":
        self._rotor_order = self._unpack_sequence(rotor_order)
        return self

    def rings(self, *ring_settings: int | Sequence[int]) -> "EnigmaConfigBuilder":
        self._ring_settings = self._unpack_sequence(ring_settings)
        return self

    def key(self, value: str) -> "EnigmaConfigBuilder":
        self._key = value
        return self

    def reflector(
        self, value: str | ReflectorName
    ) -> "EnigmaConfigBuilder":
        self._reflector_name = value
        return self

    def plugboard(
        self, pairs: Sequence[tuple[str, str]] | None
    ) -> "EnigmaConfigBuilder":
        self._plugboard_pairs = pairs or ()
        return self

    def greek(self, value: str) -> "EnigmaConfigBuilder":
        self._greek_rotor = value
        return self

    def build(self) -> EnigmaConfig:
        strategy = mode_strategy_for(self._mode)
        ring_settings = self._ring_settings
        if ring_settings is None:
            ring_settings = (
                DEFAULT_M4_RINGS
                if strategy.rotor_count() == 4
                else DEFAULT_RINGS
            )

        config = EnigmaConfig(
            text=self._text.upper(),
            mode=strategy.name,
            rotor_order=_validate_moving_rotors(self._rotor_order),
            ring_settings=_validate_ring_settings(ring_settings),
            positions=parse_key_positions(self._key, strategy.rotor_count()),
            reflector_name=_normalize_reflector_name(self._reflector_name),
            plugboard_pairs=tuple(self._plugboard_pairs),
            greek_rotor=_normalize_rotor_name(self._greek_rotor),
            mode_strategy=strategy,
        )
        self._validate_common(config)
        strategy.validate(config)
        Plugboard(config.plugboard_pairs)
        return config

    @staticmethod
    def _unpack_sequence(values: Iterable[object]) -> Sequence[object]:
        values = tuple(values)
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            return values[0]
        return values

    @staticmethod
    def _validate_common(config: EnigmaConfig) -> None:
        if config.reflector_name not in REFLECTORS:
            raise ValueError(f"Unknown reflector: {config.reflector_name}")
        if config.greek_rotor not in ROTOR_SPECS:
            raise ValueError(f"Unknown Greek rotor: {config.greek_rotor}")
