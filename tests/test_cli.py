"""CLI command tests."""

from __future__ import annotations

import builtins
from collections.abc import Iterator

import pytest

from enigma.cli import DailyKeySheetCommand


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
