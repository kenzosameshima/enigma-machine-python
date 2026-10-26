"""Shared test helpers."""

from __future__ import annotations

from enigma.alphabet import letter_to_index
from enigma.data import ROTOR_SPECS
from enigma.rotors import Rotor, RotorState


def make_rotor(
    name: str,
    *,
    can_step: bool = True,
    ring_setting: int = 1,
    position: str = "A",
) -> Rotor:
    """Build a Rotor by spec name, the way the old by-name constructor did."""

    return Rotor(
        ROTOR_SPECS[name],
        RotorState(ring=ring_setting - 1, position=letter_to_index(position)),
        can_step=can_step,
    )
