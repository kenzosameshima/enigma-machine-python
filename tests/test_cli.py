"""CLI command tests."""

from __future__ import annotations

import builtins
from collections.abc import Iterator

import pytest

from enigma.cli import DailyKeySheetCommand, M4Command, ThreeRotorCommand
from enigma.modes import MachineModeName, ReflectorName


def test_three_rotor_command_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs: Iterator[str] = iter(
        ["HELLO WORLD", "KQF", "V III II", "2 13 26", "B", "AZ BY"]
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

    output = ThreeRotorCommand(MachineModeName.NAVAL, ReflectorName.C).execute()

    assert output == (
        "\nRotor window: [KQF]\nEncrypted:  FXTTJ PMTAT\nDecrypted:  HELLO WORLD"
    )


def test_m4_command_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs: Iterator[str] = iter(
        ["HELLO WORLD", "ZKQF", "V III II", "7 2 13 26", "GAMMA", "C_THIN", "AZ BY"]
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

    output = M4Command().execute()

    assert output == (
        "\nRotor window: [ZKQ F]\nEncrypted:  KLTXE LRMDX\nDecrypted:  HELLO WORLD"
    )


def test_daily_key_sheet_command_generates_valid_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs: Iterator[str] = iter(
        [
            "I II III",
            "1 1 1",
            "",
            "",
            "AAA",
            "ABC",
            "HELLO",
        ]
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

    output = DailyKeySheetCommand().execute()

    assert "Rotor order: I II III" in output
    assert "Ring settings: 1 1 1" in output
    assert "Decrypted: HELLO" in output
