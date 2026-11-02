"""Shared test helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypedDict

from enigma.alphabet import letter_to_index
from enigma.config import EnigmaConfig
from enigma.data import ROTOR_SPECS
from enigma.machine import EnigmaMachine
from enigma.modes import MachineModeName, mode_name_for
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


def make_machine(  # noqa: PLR0913 -- one named setting per Enigma config field
    *,
    key: str = "AAA",
    mode: MachineModeName | str = MachineModeName.WEHRMACHT,
    rotor_order: tuple[str, ...] = ("I", "II", "III"),
    ring_settings: tuple[int, ...] = (1, 1, 1),
    reflector_name: str = "B",
    plug_pairs: tuple[tuple[str, str], ...] = (),
    greek_rotor_name: str = "BETA",
) -> EnigmaMachine:
    """Build a machine from an EnigmaConfig with these settings."""

    config = EnigmaConfig(
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        key=key,
        reflector_name=reflector_name,
        plugboard_pairs=plug_pairs,
        greek_rotor_name=greek_rotor_name,
        mode=mode_name_for(mode),
    )
    return EnigmaMachine.from_config(config)


class RequiredProcessArguments(TypedDict):
    text: str
    key: str


class ProcessArguments(RequiredProcessArguments, total=False):
    mode: str
    plug_pairs: Sequence[tuple[str, str]] | None
    rotor_order: Sequence[str]
    ring_settings: Sequence[int]
    reflector_name: str
    greek_rotor_name: str
