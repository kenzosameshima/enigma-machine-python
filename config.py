"""Compatibility wrapper for static Enigma configuration imports."""

from enigma.data import REFLECTORS, ROTOR_SPECS
from enigma.modes import MachineModeName, ReflectorName
from enigma.rotors import RotorSpec

__all__ = [
    "MachineModeName",
    "REFLECTORS",
    "ROTOR_SPECS",
    "ReflectorName",
    "RotorSpec",
]
