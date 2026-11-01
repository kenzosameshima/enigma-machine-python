"""Characterization tests pinning ciphertext from the current implementation.

These are regression vectors, not historical reference vectors: the expected
values were captured from this codebase as it stood before the Zen-of-Python
refactor, specifically to guard against accidental behavior changes while the
internals are restructured. They are not independently verified against a
real Enigma machine (see test_engine.py for vectors that are).
"""

from __future__ import annotations

import pytest

from enigma import enigma_process


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        (
            {
                "text": ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHEQUICKBROWNFOXAGAIN"),
                "key": "AEA",
                "mode": "wehrmacht",
                "rotor_order": ("I", "II", "III"),
                "ring_settings": (1, 1, 1),
                "reflector_name": "B",
            },
            "LYCMWLAAGDESDDNVXOLLKEUGPLKIYYSITRVPKVNOCBYQHWUFQPCESGYYPQL",
        ),
        (
            {
                "text": "ATTACK AT DAWN, REPEAT: 0600 HOURS! PROCEED NORTH-EAST.",
                "key": "XYZ",
                "mode": "naval",
                "rotor_order": ("IV", "V", "I"),
                "ring_settings": (5, 12, 19),
                "reflector_name": "C",
                "plug_pairs": [("Q", "W"), ("E", "R"), ("T", "Y")],
            },
            "TQJRGD RN LTDX, NPKLXN: 0600 VILOL! TJFUWYN HUXSA-QSYA.",
        ),
        (
            {
                "text": (
                    "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG, AGAIN AND AGAIN! 123"
                ),
                "key": "QRST",
                "mode": "m4",
                "rotor_order": ("II", "IV", "V"),
                "ring_settings": (7, 3, 21, 11),
                "reflector_name": "C_THIN",
                "greek_rotor_name": "GAMMA",
                "plug_pairs": [("A", "F"), ("G", "H"), ("I", "J"), ("K", "L")],
            },
            "LSM FMNYN PGKNQ LHH OHLGO EBLY QGL TTRG JFT, GKYEF KFB NEXVK! 123",
        ),
        (
            {
                "text": "SECRETMESSAGECROSSINGTURNOVERSANDTHEDOUBLESTEPREPEATEDLYXYZ",
                "key": "AEAB",
                "mode": "m4",
                "rotor_order": ("I", "II", "III"),
                "ring_settings": (1, 1, 1, 1),
                "reflector_name": "B_THIN",
                "greek_rotor_name": "BETA",
            },
            "CDVECDHSRDBDAEVNBZKQVGSBGJLXDQGXGDPBHVVISSULAGPPQXDWFQEVHJC",
        ),
        (
            {
                "text": "12:34 - HELLO, WORLD! (TEST) #99 / END.",
                "key": "MCK",
                "mode": "wehrmacht",
                "rotor_order": ("III", "II", "I"),
                "ring_settings": (26, 1, 14),
                "reflector_name": "B",
            },
            "12:34 - VLUES, URMVA! (LZNA) #99 / DSC.",
        ),
    ],
    ids=[
        "wehrmacht_double_step_long_message",
        "naval_nondefault_rings_plugboard_punctuation",
        "m4_gamma_cthin_plugboard_long_message",
        "m4_beta_double_step_bthin",
        "mostly_punctuation_and_digits",
    ],
)
def test_pinned_ciphertext_matches_current_implementation(
    kwargs: dict[str, object],
    expected: str,
) -> None:
    assert enigma_process(**kwargs) == expected


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "text": ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHEQUICKBROWNFOXAGAIN"),
            "key": "AEA",
            "mode": "wehrmacht",
            "rotor_order": ("I", "II", "III"),
            "ring_settings": (1, 1, 1),
            "reflector_name": "B",
        },
        {
            "text": "ATTACK AT DAWN, REPEAT: 0600 HOURS! PROCEED NORTH-EAST.",
            "key": "XYZ",
            "mode": "naval",
            "rotor_order": ("IV", "V", "I"),
            "ring_settings": (5, 12, 19),
            "reflector_name": "C",
            "plug_pairs": [("Q", "W"), ("E", "R"), ("T", "Y")],
        },
        {
            "text": (
                "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG, AGAIN AND AGAIN! 123"
            ),
            "key": "QRST",
            "mode": "m4",
            "rotor_order": ("II", "IV", "V"),
            "ring_settings": (7, 3, 21, 11),
            "reflector_name": "C_THIN",
            "greek_rotor_name": "GAMMA",
            "plug_pairs": [("A", "F"), ("G", "H"), ("I", "J"), ("K", "L")],
        },
        {
            "text": "SECRETMESSAGECROSSINGTURNOVERSANDTHEDOUBLESTEPREPEATEDLYXYZ",
            "key": "AEAB",
            "mode": "m4",
            "rotor_order": ("I", "II", "III"),
            "ring_settings": (1, 1, 1, 1),
            "reflector_name": "B_THIN",
            "greek_rotor_name": "BETA",
        },
        {
            "text": "12:34 - HELLO, WORLD! (TEST) #99 / END.",
            "key": "MCK",
            "mode": "wehrmacht",
            "rotor_order": ("III", "II", "I"),
            "ring_settings": (26, 1, 14),
            "reflector_name": "B",
        },
    ],
    ids=[
        "wehrmacht_double_step_long_message",
        "naval_nondefault_rings_plugboard_punctuation",
        "m4_gamma_cthin_plugboard_long_message",
        "m4_beta_double_step_bthin",
        "mostly_punctuation_and_digits",
    ],
)
def test_pinned_ciphertext_round_trips_to_original_text(
    kwargs: dict[str, object],
) -> None:
    encrypted = enigma_process(**kwargs)
    decrypt_kwargs = dict(kwargs)
    decrypt_kwargs["text"] = encrypted
    decrypted = enigma_process(**decrypt_kwargs)

    assert decrypted == str(kwargs["text"]).upper()
