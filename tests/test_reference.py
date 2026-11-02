"""Published vectors and explicitly labeled independent-model comparisons."""

from itertools import permutations

import pytest
from reference_enigma import TURNOVER, reference_process

from enigma import enigma_process


@pytest.mark.parametrize("order", list(permutations(("I", "II", "III", "IV", "V"), 3)))
def test_every_order_against_independent_contacts(order: tuple[str, str, str]) -> None:
    key = "A" + TURNOVER[order[1]] + TURNOVER[order[2]]
    rings = (26, 13, 2)
    text = "AZBYCXDW"
    expected = reference_process(
        text, order=order, windows=key, rings=rings, reflector="C"
    )
    assert (
        enigma_process(
            text, key, rotor_order=order, ring_settings=rings, reflector_name="C"
        )
        == expected
    )


# Published examples, including rings, plugboard, turnover and double-step:
# https://kerryb.github.io/enigma/#test-cases
# M3 I-V/B share Enigma I wiring: https://www.cryptomuseum.com/crypto/enigma/wiring.htm
@pytest.mark.parametrize("mode", ["wehrmacht", "naval"])
@pytest.mark.parametrize(
    ("rings", "key", "pairs", "expected"),
    [
        ((1, 1, 1), "AAA", (), "MFNCZBBFZM"),
        ((20, 13, 5), "AAA", (), "JCEESPSDYR"),
        ((1, 1, 1), "AAA", (("C", "Q"), ("X", "P")), "MFNQZBBFZM"),
        ((1, 1, 1), "AEQ", (), "NIJMQPUDGW"),
        ((1, 1, 1), "ADP", (), "XUWJPJIBIE"),
    ],
)
def test_published_vectors_also_anchor_reference_model(
    mode: str,
    rings: tuple[int, ...],
    key: str,
    pairs: tuple[tuple[str, str], ...],
    expected: str,
) -> None:
    assert (
        reference_process(
            "HELLOWORLD",
            order=("III", "II", "I"),
            rings=rings,
            windows=key,
            reflector="B",
            pairs=pairs,
        )
        == expected
    )
    assert (
        enigma_process(
            "HELLOWORLD",
            key,
            mode=mode,
            rotor_order=("III", "II", "I"),
            ring_settings=rings,
            plug_pairs=pairs,
        )
        == expected
    )


@pytest.mark.parametrize("greek", ["BETA", "GAMMA"])
@pytest.mark.parametrize("reflector", ["B_THIN", "C_THIN"])
@pytest.mark.parametrize("rings", [(1, 1, 1, 1), (26, 13, 2, 7)])
def test_m4_differential_across_turnover(
    greek: str, reflector: str, rings: tuple[int, ...]
) -> None:
    # Differential oracle, not a claimed historical M4 known-answer vector.
    text = "aßz! " + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 3
    pairs = (("A", "Z"), ("B", "Y"), ("C", "X"))
    expected = reference_process(
        text,
        order=(greek, "I", "II", "III"),
        windows="QADU",
        rings=(rings[3], *rings[:3]),
        reflector=reflector,
        pairs=pairs,
    )
    assert (
        enigma_process(
            text,
            "ADUQ",
            mode="m4",
            ring_settings=rings,
            reflector_name=reflector,
            greek_rotor_name=greek,
            plug_pairs=pairs,
        )
        == expected
    )


@pytest.mark.parametrize("mode", ["wehrmacht", "naval"])
@pytest.mark.parametrize("reflector", ["B", "C"])
@pytest.mark.parametrize("rings", [(2, 13, 26), (26, 2, 13)])
def test_three_rotor_differential_nondefault_ring_double_step(
    mode: str,
    reflector: str,
    rings: tuple[int, ...],
) -> None:
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 3
    pairs = (("A", "Z"), ("B", "Y"))
    expected = reference_process(
        text,
        order=("I", "II", "III"),
        windows="ADU",
        rings=rings,
        reflector=reflector,
        pairs=pairs,
    )
    assert (
        enigma_process(
            text,
            "ADU",
            mode=mode,
            ring_settings=rings,
            reflector_name=reflector,
            plug_pairs=pairs,
        )
        == expected
    )
