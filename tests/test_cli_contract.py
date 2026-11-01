"""Interactive input/output contracts, with errors terminating the current command."""

import builtins
import re
from collections.abc import Callable

import pytest

from enigma import cli
from enigma.modes import MachineModeName, ReflectorName


def feed(monkeypatch: pytest.MonkeyPatch, answers: list[str]) -> list[str]:
    iterator = iter(answers)
    prompts: list[str] = []

    def answer(prompt: str = "") -> str:
        prompts.append(prompt)
        return next(iterator)

    monkeypatch.setattr(builtins, "input", answer)
    return prompts


@pytest.mark.parametrize("mode", ["1", "2", "3"])
def test_main_happy_path(
    mode: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    m4 = mode == "3"
    answers = [mode, "hello world", "AAAA" if m4 else "AAA", "", ""]
    if m4:
        answers.append("")
    answers += ["", ""]
    prompts = feed(monkeypatch, answers)
    cli.main()
    output = capsys.readouterr().out
    assert ("Rotor window: [AAA A]" if m4 else "Rotor window: [AAA]") in output
    assert "Decrypted:  HELLO WORLD" in output
    assert "Encrypted:  " in output
    assert len(prompts) == len(answers)
    assert "Configuration error:" not in output


def test_daily_key_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # B/D/Z encodes AAA with I-II-III, UKW-B and AAA; also derived from
    # the published wiring in tests/reference_enigma.py, not pinned from production.
    answers = ["0", "", "", "", "", "AAA", "BDZ", "hello"]
    prompts = feed(monkeypatch, answers)
    cli.main()
    output = capsys.readouterr().out
    assert "Message key decrypted: AAA" in output
    assert "Decrypted: HELLO" in output
    assert len(prompts) == len(answers)


def test_main_invalid_choice_exits(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    prompts = feed(monkeypatch, ["invalid"])
    cli.main()
    assert capsys.readouterr().out.endswith("Invalid choice.\n")
    assert len(prompts) == 1


@pytest.mark.parametrize("mode", ["0", "1", "2", "3"])
def test_main_configuration_error_exits_without_reprompt(
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    answers = [mode, "I II"] if mode == "0" else [mode, "hello", "AAA", "I II"]
    prompts = feed(monkeypatch, answers)
    cli.main()
    assert capsys.readouterr().out.endswith(
        "Configuration error: Rotor order must contain exactly 3 moving rotors\n"
    )
    assert len(prompts) == len(answers)


@pytest.mark.parametrize(
    ("prompt", "answer", "message"),
    [
        (
            cli.prompt_rotor_order,
            "I II",
            "Rotor order must contain exactly 3 moving rotors",
        ),
        (
            cli.prompt_rotor_order,
            "I II VI",
            "Rotor order must use I, II, III, IV, or V",
        ),
        (cli.prompt_rotor_order, "I II II", "Rotor order cannot repeat rotors"),
        (lambda: cli.prompt_ring_settings(3), "1 2", "Expected 3 ring settings"),
        (lambda: cli.prompt_ring_settings(3), "1 x 3", "Ring settings must be numeric"),
        (
            lambda: cli.prompt_ring_settings(3),
            "0 1 1",
            "Ring settings must be between 1 and 26",
        ),
        (
            lambda: cli.prompt_ring_settings(3),
            "1 27 1",
            "Ring settings must be between 1 and 26",
        ),
        (cli.prompt_plugboard, "ABC", "Invalid plugboard pair: ABC"),
        (cli.prompt_plugboard, "1A", "Invalid plugboard pair: 1A"),
        (cli.prompt_plugboard, "A1", "Invalid plugboard pair: A1"),
        (cli.prompt_greek_rotor, "I", "Greek rotor must be BETA or GAMMA"),
        (
            lambda: cli.prompt_reflector(
                "Reflector: ", ReflectorName.B, {ReflectorName.B, ReflectorName.C}
            ),
            "D",
            "Reflector must be one of: B, C",
        ),
    ],
)
def test_invalid_prompt_branch(
    prompt: Callable[[], object],
    answer: str,
    message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = feed(monkeypatch, [answer])
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        prompt()
    assert len(prompts) == 1


@pytest.mark.parametrize(
    ("command", "answers"),
    [
        (
            cli.ThreeRotorCommand(MachineModeName.WEHRMACHT, ReflectorName.B),
            ["", "AAA", "", "", "", ""],
        ),
        (cli.M4Command(), ["", "AAAA", "", "", "", "", ""]),
        (cli.DailyKeySheetCommand(), ["", "", "", "", "AAA", "BDZ", ""]),
    ],
)
def test_command_empty_message(
    command: cli.CliCommand, answers: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    feed(monkeypatch, answers)
    output = command.execute()
    if isinstance(command, cli.DailyKeySheetCommand):
        assert output == "No message entered."
    else:
        assert output.endswith("Encrypted:  \nDecrypted:  ")


def test_cli_normalizes_names_and_separators(monkeypatch: pytest.MonkeyPatch) -> None:
    feed(monkeypatch, [" iii, ii, i ", "1, 26, 2", " az, by ", " gamma "])
    assert cli.prompt_rotor_order() == ("III", "II", "I")
    assert cli.prompt_ring_settings(3) == (1, 26, 2)
    assert cli.prompt_plugboard() == (("A", "Z"), ("B", "Y"))
    assert cli.prompt_greek_rotor() == "GAMMA"


@pytest.mark.xfail(strict=True, reason="CLI must preserve input until ASCII validation")
@pytest.mark.parametrize("pair", ["\u0131Z", "\u017fZ", "Z\u0131", "Z\u017f"])
def test_cli_rejects_unicode_plug_aliases(
    pair: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    feed(monkeypatch, [pair])
    with pytest.raises(
        ValueError, match=f"^Invalid plugboard pair: {re.escape(pair)}$"
    ):
        cli.prompt_plugboard()
