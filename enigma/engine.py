"""Public engine helpers kept for programmatic use and compatibility."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import DEFAULT_RINGS, DEFAULT_ROTORS
from .config import EnigmaConfigBuilder
from .factory import EnigmaFactory
from .machine import EnigmaMachine
from .modes import MachineModeName, ReflectorName
from .plugboard import Plugboard, normalize_pair
from .rotors import Rotor

__all__ = [
    "enigma_process",
    "normalize_pairs",
    "step_rotors",
]


def normalize_pairs(pairs: Sequence[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    """Validate and normalize plugboard pairs."""

    Plugboard(pairs)
    return tuple(normalize_pair(pair) for pair in pairs)


def step_rotors(rotors: Sequence[Rotor]) -> None:
    """Compatibility helper for callers that used the old function."""

    EnigmaMachine(
        rotors,
        ReflectorName.B.value,
        Plugboard(),
        copy_rotors=False,
    ).step_rotors()


def enigma_process(
    text: str,
    key: str,
    mode: str = MachineModeName.WEHRMACHT.value,
    plug_pairs: Sequence[tuple[str, str]] | None = None,
    rotor_order: Sequence[str] = DEFAULT_ROTORS,
    ring_settings: Sequence[int] = DEFAULT_RINGS,
    reflector_name: str = ReflectorName.B.value,
    greek_rotor_name: str = "BETA",
) -> str:
    """Build a configured Enigma machine and process text.

    The function returns uppercase Enigma output for alphabetic input, preserves
    non-alphabetic characters, and advances rotors only for A-Z characters.
    Invalid modes, rotors, ring settings, keys, reflectors, Greek rotors, or
    plugboard pairs raise ValueError.
    """

    config = (
        EnigmaConfigBuilder()
        .text(text)
        .mode(mode)
        .rotors(rotor_order)
        .rings(ring_settings)
        .key(key)
        .reflector(reflector_name)
        .plugboard(plug_pairs)
        .greek(greek_rotor_name)
        .build()
    )
    machine = EnigmaFactory().create(config)
    return machine.process_text(config.text)
