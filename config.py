"""
Compatibility wrapper.

The canonical implementation lives in enigma.config.
This module is kept to avoid breaking older imports.
"""

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
