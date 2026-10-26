"""Compatibility tests for legacy wrappers and helper functions."""

from __future__ import annotations

import unittest

import pytest
from helpers import make_rotor

from enigma import enigma_process
from enigma.engine import step_rotors


def test_step_rotors_compat_helper_still_mutates_passed_rotors() -> None:
    rotors = [make_rotor("I"), make_rotor("II"), make_rotor("III")]

    step_rotors(rotors)

    assert "".join(rotor.get_position_letter() for rotor in rotors) == "AAB"


def test_step_rotors_rejects_incorrect_moving_rotor_count() -> None:
    with pytest.raises(ValueError, match="exactly 3 moving rotors"):
        step_rotors([make_rotor("I"), make_rotor("II")])


class UnittestCompatibilityTests(unittest.TestCase):
    def test_enigma_process_round_trip(self) -> None:
        encrypted = enigma_process("HELLO WORLD", "ABC")
        decrypted = enigma_process(encrypted, "ABC")

        self.assertEqual(decrypted, "HELLO WORLD")
