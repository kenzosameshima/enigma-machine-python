"""Compatibility wrapper for the package engine API."""

from enigma.alphabet import BASE, DEFAULT_RINGS, DEFAULT_ROTORS
from enigma.config import EnigmaConfig, EnigmaConfigBuilder, parse_key_positions
from enigma.engine import (
    enigma_process,
    normalize_pairs,
    plugboard_swap,
    process_char,
    step_rotors,
)
from enigma.factory import EnigmaFactory
from enigma.machine import EnigmaMachine
from enigma.modes import (
    M4Mode,
    MachineMode,
    MachineModeName,
    ReflectorName,
    ThreeRotorMode,
    mode_strategy_for,
)
from enigma.observer import EnigmaObserver
from enigma.plugboard import Plugboard
from enigma.rotors import Rotor, RotorSpec, RotorState

__all__ = [
    "BASE",
    "DEFAULT_RINGS",
    "DEFAULT_ROTORS",
    "EnigmaConfig",
    "EnigmaConfigBuilder",
    "EnigmaFactory",
    "EnigmaMachine",
    "EnigmaObserver",
    "M4Mode",
    "MachineMode",
    "MachineModeName",
    "Plugboard",
    "ReflectorName",
    "Rotor",
    "RotorSpec",
    "RotorState",
    "ThreeRotorMode",
    "enigma_process",
    "mode_strategy_for",
    "normalize_pairs",
    "parse_key_positions",
    "plugboard_swap",
    "process_char",
    "step_rotors",
]
