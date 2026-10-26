"""Configuration model and builder for Enigma machines."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import TypeVar, cast

from .alphabet import (
    DEFAULT_M4_RINGS,
    DEFAULT_POSITIONS,
    DEFAULT_RINGS,
    DEFAULT_ROTORS,
    MOVING_ROTORS,
    is_base_letter,
)
from .data import REFLECTORS, ROTOR_SPECS
from .modes import (
    GreekRotorName,
    MachineMode,
    MachineModeName,
    ReflectorName,
    ThreeRotorMode,
    mode_strategy_for,
)
from .plugboard import Plugboard

T = TypeVar("T")


def _normalize_key_positions(key: str, rotor_count: int) -> str:
    if not isinstance(key, str):
        raise ValueError("Key must be text containing rotor position letters")
    normalized = "".join(ch for ch in key.upper() if is_base_letter(ch))
    if len(normalized) != rotor_count:
        raise ValueError(f"Key must contain exactly {rotor_count} letters")
    return normalized


def _normalize_rotor_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("Rotor names must be text")
    return name.strip().upper()


def _normalize_reflector_name(name: str | ReflectorName) -> str:
    if isinstance(name, ReflectorName):
        return name.value
    if not isinstance(name, str):
        raise ValueError("Reflector name must be text")
    return name.strip().upper()


def _normalize_greek_rotor(name: str | GreekRotorName) -> str:
    if isinstance(name, GreekRotorName):
        return name.value
    if not isinstance(name, str):
        raise ValueError("Greek rotor must be text")
    return name.strip().upper()


def _validate_moving_rotors(rotor_order: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(_normalize_rotor_name(name) for name in rotor_order)
    if any(name not in MOVING_ROTORS for name in normalized):
        raise ValueError("Moving rotors must be selected from I, II, III, IV, V")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Moving rotors must be unique")
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
    if config.reflector_name not in REFLECTORS:
        raise ValueError(f"Unknown reflector: {config.reflector_name}")
    if config.greek_rotor not in ROTOR_SPECS:
        raise ValueError(f"Unknown Greek rotor: {config.greek_rotor}")


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

    def __post_init__(self) -> None:
        """Validate and normalize fields identically for every construction path."""

        if not isinstance(self.text, str):
            raise ValueError("Text must be a string")

        strategy = self.mode_strategy
        if not isinstance(strategy, MachineMode):
            raise ValueError("mode_strategy must be a MachineMode instance")
        if strategy.name != self.mode:
            raise ValueError(
                f"mode {self.mode!r} does not match mode_strategy {strategy.name!r}"
            )

        object.__setattr__(
            self, "rotor_order", _validate_moving_rotors(self.rotor_order)
        )
        object.__setattr__(
            self, "ring_settings", _validate_ring_settings(self.ring_settings)
        )
        object.__setattr__(
            self,
            "positions",
            _normalize_key_positions(self.positions, strategy.rotor_count()),
        )
        object.__setattr__(
            self, "reflector_name", _normalize_reflector_name(self.reflector_name)
        )
        object.__setattr__(
            self, "greek_rotor", _normalize_greek_rotor(self.greek_rotor)
        )
        object.__setattr__(
            self,
            "plugboard_pairs",
            tuple(tuple(pair) for pair in self.plugboard_pairs),
        )

        _validate_reflector_and_greek(self)
        strategy.validate(self)
        Plugboard(self.plugboard_pairs)


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
        self._greek_rotor: str | GreekRotorName = GreekRotorName.BETA

    def text(self, value: str) -> EnigmaConfigBuilder:
        """Set input text. Text is normalized to uppercase during build."""

        self._text = value
        return self

    def mode(self, value: MachineModeName | str | MachineMode) -> EnigmaConfigBuilder:
        """Set machine mode: wehrmacht, naval, m4, or a mode strategy."""

        self._mode = value
        return self

    def rotors(self, *rotor_order: str | Sequence[str]) -> EnigmaConfigBuilder:
        """Set moving rotors left-to-right."""

        self._rotor_order = self._unpack_sequence(rotor_order)
        return self

    def rings(self, *ring_settings: int | Sequence[int]) -> EnigmaConfigBuilder:
        """Set one-based ring settings."""

        self._ring_settings = self._unpack_sequence(ring_settings)
        return self

    def key(self, value: str) -> EnigmaConfigBuilder:
        """Set initial rotor window positions."""

        self._key = value
        return self

    def reflector(self, value: str | ReflectorName) -> EnigmaConfigBuilder:
        """Set reflector name."""

        self._reflector_name = value
        return self

    def plugboard(self, pairs: Sequence[tuple[str, str]] | None) -> EnigmaConfigBuilder:
        """Set plugboard letter pairs."""

        self._plugboard_pairs = pairs or ()
        return self

    def greek(self, value: str | GreekRotorName) -> EnigmaConfigBuilder:
        """Set the fixed Greek rotor used by M4 mode."""

        self._greek_rotor = value
        return self

    def build(self) -> EnigmaConfig:
        """Validate and return an immutable configuration object."""

        strategy = mode_strategy_for(self._mode)
        ring_settings = self._ring_settings
        if ring_settings is None:
            ring_settings = (
                DEFAULT_M4_RINGS if strategy.rotor_count() == 4 else DEFAULT_RINGS
            )

        return EnigmaConfig(
            text=self._text.upper(),
            mode=strategy.name,
            rotor_order=tuple(self._rotor_order),
            ring_settings=tuple(ring_settings),
            positions=self._key,
            reflector_name=self._reflector_name,
            plugboard_pairs=tuple(self._plugboard_pairs),
            greek_rotor=self._greek_rotor,
            mode_strategy=strategy,
        )

    @staticmethod
    def _unpack_sequence(values: Iterable[T | Sequence[T]]) -> Sequence[T]:
        values = tuple(values)
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            return cast(Sequence[T], values[0])
        return cast(tuple[T, ...], values)
