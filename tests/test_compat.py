"""Compatibility tests for legacy wrappers and helper functions."""

from __future__ import annotations

import unittest

import pytest

from enigma import EnigmaConfigBuilder, EnigmaFactory, enigma_process
from enigma.engine import process_char, step_rotors
from enigma.rotors import Rotor


def make_machine(*, key: str = "AAA"):
    config = (
        EnigmaConfigBuilder()
        .text("")
        .rotors("I", "II", "III")
        .rings(1, 1, 1)
        .key(key)
        .reflector("B")
        .build()
    )
    return EnigmaFactory().create(config)


def test_legacy_engine_wrapper_still_exports_enigma_process() -> None:
    from engine import enigma_process as legacy_enigma_process

    assert legacy_enigma_process("HELLO", "AAA") == enigma_process("HELLO", "AAA")


def test_step_rotors_compat_helper_still_mutates_passed_rotors() -> None:
    rotors = [Rotor("I"), Rotor("II"), Rotor("III")]

    step_rotors(rotors)

    assert "".join(rotor.get_position_letter() for rotor in rotors) == "AAB"


def test_step_rotors_rejects_incorrect_moving_rotor_count() -> None:
    with pytest.raises(ValueError, match="exactly 3 moving rotors"):
        step_rotors([Rotor("I"), Rotor("II")])


def test_compat_process_char_encodes_without_stepping_existing_rotors() -> None:
    machine = make_machine(key="AAC")

    assert process_char("A", machine.rotors, "B") == machine.encode_signal("A")


class UnittestCompatibilityTests(unittest.TestCase):
    def test_enigma_process_round_trip(self) -> None:
        encrypted = enigma_process("HELLO WORLD", "ABC")
        decrypted = enigma_process(encrypted, "ABC")

        self.assertEqual(decrypted, "HELLO WORLD")
