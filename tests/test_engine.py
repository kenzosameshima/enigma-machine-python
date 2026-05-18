"""High-level API and known-vector regression tests."""

from __future__ import annotations

import pytest

from enigma import enigma_process


@pytest.mark.parametrize(
    ("reflector_name", "ring_settings"),
    [
        ("B", (1, 1, 1)),
        ("C", (1, 1, 1)),
        ("B", (2, 14, 26)),
    ],
)
def test_three_rotor_round_trip(
    reflector_name: str,
    ring_settings: tuple[int, ...],
) -> None:
    encrypted = enigma_process(
        text="HELLO WORLD",
        key="ABC",
        mode="wehrmacht",
        plug_pairs=[("A", "B"), ("C", "D")],
        rotor_order=("I", "II", "III"),
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )

    decrypted = enigma_process(
        text=encrypted,
        key="ABC",
        mode="wehrmacht",
        plug_pairs=[("A", "B"), ("C", "D")],
        rotor_order=("I", "II", "III"),
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )

    assert decrypted == "HELLO WORLD"


def test_m4_round_trip() -> None:
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

    assert decrypted == "ENIGMA"


def test_spaces_punctuation_and_numbers_are_preserved() -> None:
    result = enigma_process(text="HI, 42!", key="AAA")

    assert result[2:] == ", 42!"


def test_lowercase_input_is_normalized() -> None:
    assert enigma_process(text="hello", key="ABC") == enigma_process(
        text="HELLO",
        key="ABC",
    )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"text": "HELLOWORLD", "key": "AAA"}, "ILBDAAMTAZ"),
        (
            {
                "text": "HELLO, WORLD! 123",
                "key": "ABC",
                "plug_pairs": [("A", "B"), ("C", "D")],
            },
            "ROMUL, LAIAI! 123",
        ),
        (
            {
                "text": "ENIGMA",
                "key": "WXYZ",
                "mode": "m4",
                "rotor_order": ("I", "II", "III"),
                "ring_settings": (1, 1, 1, 1),
                "reflector_name": "B_THIN",
                "greek_rotor_name": "BETA",
            },
            "PKJETQ",
        ),
    ],
)
def test_index_conversion_refactor_preserves_known_outputs(
    kwargs: dict[str, object],
    expected: str,
) -> None:
    assert enigma_process(**kwargs) == expected


@pytest.mark.parametrize(
    ("rotors", "rings", "key", "plug_pairs", "expected"),
    [
        (("III", "II", "I"), (1, 1, 1), "AAA", (), "MFNCZBBFZM"),
        (("I", "III", "II"), (1, 1, 1), "AAA", (), "ZXVMIZYFEY"),
        (("III", "II", "I"), (1, 1, 1), "JXB", (), "QNDMFRCGTS"),
        (
            ("III", "II", "I"),
            (1, 1, 1),
            "AAA",
            (("C", "Q"), ("X", "P")),
            "MFNQZBBFZM",
        ),
        (("III", "II", "I"), (20, 13, 5), "AAA", (), "JCEESPSDYR"),
        (("III", "II", "I"), (1, 1, 1), "AEQ", (), "NIJMQPUDGW"),
        (("III", "II", "I"), (1, 1, 1), "ADP", (), "XUWJPJIBIE"),
    ],
)
def test_enigma_i_reference_vectors(
    rotors: tuple[str, str, str],
    rings: tuple[int, int, int],
    key: str,
    plug_pairs: tuple[tuple[str, str], ...],
    expected: str,
) -> None:
    """Verify Enigma I examples from https://kerryb.github.io/enigma/."""

    assert (
        enigma_process(
            text="HELLOWORLD",
            key=key,
            rotor_order=rotors,
            ring_settings=rings,
            plug_pairs=plug_pairs,
            reflector_name="B",
        )
        == expected
    )


def test_plugboard_with_valid_pairs_changes_output_but_round_trips() -> None:
    encrypted = enigma_process(
        text="PLUGBOARD",
        key="MCK",
        plug_pairs=[("P", "O"), ("L", "U")],
    )
    decrypted = enigma_process(
        text=encrypted,
        key="MCK",
        plug_pairs=[("P", "O"), ("L", "U")],
    )

    assert encrypted != "PLUGBOARD"
    assert decrypted == "PLUGBOARD"


def test_enigma_process_does_not_reuse_mutable_machine_state() -> None:
    first = enigma_process("AAAA", "AAA")
    second = enigma_process("AAAA", "AAA")

    assert first == second


def test_enigma_process_rejects_unknown_mode_with_predictable_message() -> None:
    with pytest.raises(ValueError, match="Unsupported machine mode: commercial"):
        enigma_process(text="HELLO", key="AAA", mode="commercial")
