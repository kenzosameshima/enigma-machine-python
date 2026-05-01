"""Regression tests for Enigma processing."""

import unittest

from enigma import EnigmaConfigBuilder, EnigmaFactory, enigma_process
from enigma.modes import MachineModeName
from enigma.plugboard import Plugboard


class EnigmaProcessTests(unittest.TestCase):
    def test_three_rotor_round_trip_with_plugboard(self) -> None:
        encrypted = enigma_process(
            text="HELLO WORLD",
            key="ABC",
            mode="wehrmacht",
            plug_pairs=[("A", "B"), ("C", "D")],
            rotor_order=("I", "II", "III"),
            ring_settings=(1, 1, 1),
            reflector_name="B",
        )

        decrypted = enigma_process(
            text=encrypted,
            key="ABC",
            mode="wehrmacht",
            plug_pairs=[("A", "B"), ("C", "D")],
            rotor_order=("I", "II", "III"),
            ring_settings=(1, 1, 1),
            reflector_name="B",
        )

        self.assertEqual(decrypted, "HELLO WORLD")

    def test_m4_round_trip(self) -> None:
        encrypted = enigma_process(
            text="ENIGMA",
            key="WXYZ",
            mode="m4",
            rotor_order=("I", "II", "III"),
            ring_settings=(1, 1, 1, 1),
            reflector_name="B_THIN",
            greek_rotor_name="BETA",
        )

        decrypted = enigma_process(
            text=encrypted,
            key="WXYZ",
            mode="m4",
            rotor_order=("I", "II", "III"),
            ring_settings=(1, 1, 1, 1),
            reflector_name="B_THIN",
            greek_rotor_name="BETA",
        )

        self.assertEqual(decrypted, "ENIGMA")


class BuilderAndFactoryTests(unittest.TestCase):
    def test_builder_creates_machine_with_expected_window(self) -> None:
        config = (
            EnigmaConfigBuilder()
            .text("HELLO")
            .mode(MachineModeName.WEHRMACHT)
            .rotors(("I", "II", "III"))
            .rings((1, 1, 1))
            .key("ABC")
            .reflector("B")
            .build()
        )

        machine = EnigmaFactory().create(config)

        self.assertEqual(machine.window(), "ABC")

    def test_plugboard_rejects_reused_letters(self) -> None:
        with self.assertRaises(ValueError):
            Plugboard([("A", "B"), ("A", "C")])


if __name__ == "__main__":
    unittest.main()
