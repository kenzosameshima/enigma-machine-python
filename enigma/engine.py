"""Programmatic entry point for running text through a configured machine."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import DEFAULT_RINGS, DEFAULT_ROTORS
from .config import EnigmaConfig
from .machine import EnigmaMachine
from .modes import MachineModeName, ReflectorName, mode_name_for

__all__ = ["enigma_process"]


def enigma_process(  # noqa: PLR0913, PLR0917 -- public signature, kept stable
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

    config = EnigmaConfig(
        rotor_order=tuple(rotor_order),
        ring_settings=tuple(ring_settings),
        key=key,
        reflector_name=reflector_name,
        plugboard_pairs=tuple(plug_pairs or ()),
        greek_rotor_name=greek_rotor_name,
        mode=mode_name_for(mode),
    )
    machine = EnigmaMachine.from_config(config)
    return machine.process_text(text)
