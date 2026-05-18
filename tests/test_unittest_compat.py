"""Minimal unittest compatibility checks for the legacy test command."""

from __future__ import annotations

import unittest

from enigma import enigma_process


class UnittestCompatibilityTests(unittest.TestCase):
    def test_enigma_process_round_trip(self) -> None:
        encrypted = enigma_process("HELLO WORLD", "ABC")
        decrypted = enigma_process(encrypted, "ABC")

        self.assertEqual(decrypted, "HELLO WORLD")


if __name__ == "__main__":
    unittest.main()
