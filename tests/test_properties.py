"""Cipher properties, exhaustive small domains and generated full configurations."""

import itertools
import string

import pytest
from helpers import make_machine, make_rotor
from hypothesis import given, settings
from hypothesis import strategies as st

from enigma import EnigmaConfig, EnigmaMachine, Plugboard
from enigma.modes import MachineModeName

ORDERS = list(itertools.permutations(("I", "II", "III", "IV", "V"), 3))
NOTCHES = {"I": "Q", "II": "E", "III": "V", "IV": "J", "V": "Z"}
MODES = [
    (MachineModeName.WEHRMACHT, "B", "BETA"),
    (MachineModeName.WEHRMACHT, "C", "BETA"),
    (MachineModeName.NAVAL, "B", "BETA"),
    (MachineModeName.NAVAL, "C", "BETA"),
    (MachineModeName.M4, "B_THIN", "BETA"),
    (MachineModeName.M4, "C_THIN", "BETA"),
    (MachineModeName.M4, "B_THIN", "GAMMA"),
    (MachineModeName.M4, "C_THIN", "GAMMA"),
]


@pytest.mark.parametrize("order", ORDERS)
@pytest.mark.parametrize(("mode", "reflector", "greek"), MODES)
def test_every_order_and_reflector_is_reciprocal_without_fixed_points(
    order: tuple[str, str, str],
    mode: MachineModeName,
    reflector: str,
    greek: str,
) -> None:
    m4 = mode is MachineModeName.M4
    machine = make_machine(
        rotor_order=order,
        key="ADVQ" if m4 else "ADV",
        mode=mode,
        reflector_name=reflector,
        greek_rotor_name=greek,
        ring_settings=(2, 13, 26, 7) if m4 else (2, 13, 26),
        plug_pairs=(("A", "Z"), ("B", "Y")),
    )
    text = string.ascii_uppercase
    ciphertext = machine.process_text(text)
    assert all(a != b for a, b in zip(text, ciphertext, strict=True))
    machine.reset()
    assert machine.process_text(ciphertext) == text


@st.composite
def configs(draw: st.DrawFn) -> EnigmaConfig:
    mode, reflector, greek = draw(st.sampled_from(MODES))
    count = 4 if mode is MachineModeName.M4 else 3
    letters = draw(
        st.lists(st.sampled_from(string.ascii_uppercase), unique=True, max_size=20)
    )
    pairs = tuple(zip(letters[::2], letters[1::2], strict=False))
    return EnigmaConfig(
        rotor_order=draw(st.sampled_from(ORDERS)),
        mode=mode,
        reflector_name=reflector,
        greek_rotor_name=greek,
        key=draw(st.text(string.ascii_uppercase, min_size=count, max_size=count)),
        ring_settings=tuple(
            draw(st.lists(st.integers(1, 26), min_size=count, max_size=count))
        ),
        plugboard_pairs=pairs,
    )


@settings(max_examples=80, deadline=None)
@given(
    config=configs(),
    text=st.one_of(
        st.text(max_size=80), st.text(string.ascii_letters + " 123!?", max_size=80)
    ),
    split=st.integers(0, 80),
)
def test_generated_text_preserves_contract(
    config: EnigmaConfig,
    text: str,
    split: int,
) -> None:
    normalized = text.translate(
        str.maketrans(string.ascii_lowercase, string.ascii_uppercase)
    )
    machine = EnigmaMachine.from_config(config)
    initial = tuple(rotor.snapshot() for rotor in machine.rotors)
    ciphertext = machine.process_text(text)
    assert len(ciphertext) == len(text)
    for plain, encrypted in zip(normalized, ciphertext, strict=True):
        if plain in string.ascii_uppercase:
            assert encrypted in string.ascii_uppercase
            assert encrypted != plain
        else:
            assert encrypted == plain
    end = tuple(rotor.snapshot() for rotor in machine.rotors)
    machine.reset()
    assert tuple(rotor.snapshot() for rotor in machine.rotors) == initial
    assert machine.process_text(ciphertext) == normalized
    machine.reset()
    assert (
        machine.process_text(text[:split]) + machine.process_text(text[split:])
        == ciphertext
    )
    assert tuple(rotor.snapshot() for rotor in machine.rotors) == end
    machine.reset()
    machine.process_text("".join(c for c in normalized if c in string.ascii_uppercase))
    assert tuple(rotor.snapshot() for rotor in machine.rotors) == end
    board = Plugboard(config.plugboard_pairs)
    assert all(board.swap(board.swap(c)) == c for c in string.ascii_uppercase)


@pytest.mark.parametrize("name", ["I", "II", "III", "IV", "V", "BETA", "GAMMA"])
def test_rotor_inverse_permutations_for_every_ring_and_position(name: str) -> None:
    for ring, position in itertools.product(range(1, 27), string.ascii_uppercase):
        rotor = make_rotor(name, ring_setting=ring, position=position)
        forward = [rotor.encode_forward(i) for i in range(26)]
        backward = [rotor.encode_backward(i) for i in range(26)]
        assert sorted(forward) == list(range(26))
        assert sorted(backward) == list(range(26))
        assert [backward[i] for i in forward] == list(range(26))
        assert [forward[i] for i in backward] == list(range(26))


@pytest.mark.parametrize(("name", "notch"), list(NOTCHES.items()))
def test_notch_is_fixed_for_every_ring_and_window(name: str, notch: str) -> None:
    for ring, position in itertools.product(range(1, 27), string.ascii_uppercase):
        rotor = make_rotor(name, ring_setting=ring, position=position)
        assert rotor.at_notch() is (position == notch)


@pytest.mark.parametrize("order", ORDERS)
def test_turnover_and_double_step_with_nondefault_rings(
    order: tuple[str, str, str],
) -> None:
    middle_notch = NOTCHES[order[1]]
    right_notch = NOTCHES[order[2]]
    before_middle = string.ascii_uppercase[(ord(middle_notch) - ord("A") - 1) % 26]
    before_right = string.ascii_uppercase[(ord(right_notch) - ord("A") - 1) % 26]
    machine = make_machine(
        rotor_order=order,
        key="A" + before_middle + before_right,
        ring_settings=(26, 13, 2),
    )
    advances = []
    for _ in range(4):
        old = tuple(rotor.position for rotor in machine.rotors)
        middle_at_notch = machine.window()[1] == middle_notch
        machine.step_rotors()
        new = tuple(rotor.position for rotor in machine.rotors)
        movement = tuple((b - a) % 26 for a, b in zip(old, new, strict=True))
        assert (movement[0] == 1) is middle_at_notch
        if middle_at_notch:
            assert movement[1] == 1
        advances.append(movement)
    assert advances == [(0, 0, 1), (0, 1, 1), (1, 1, 1), (0, 0, 1)]


@pytest.mark.parametrize("m4", [False, True])
def test_single_notch_period_and_twenty_six_double_steps(m4: bool) -> None:
    machine = make_machine(
        key="AAAQ" if m4 else "AAA",
        mode="m4" if m4 else "wehrmacht",
        reflector_name="B_THIN" if m4 else "B",
        ring_settings=(26, 13, 2, 7) if m4 else (26, 13, 2),
    )
    initial = machine.window()
    seen = set()
    double_steps = 0
    previous_middle_step = False
    for _ in range(16900):
        window = machine.window()
        assert window not in seen
        seen.add(window)
        old = tuple(rotor.position for rotor in machine.rotors[-3:])
        machine.step_rotors()
        new = tuple(rotor.position for rotor in machine.rotors[-3:])
        left_step, middle_step, right_step = (
            (b - a) % 26 for a, b in zip(old, new, strict=True)
        )
        assert right_step == 1
        assert (left_step == 1) is (old[1] == 4)
        if left_step:
            assert middle_step == 1
        double_steps += bool(middle_step and previous_middle_step)
        previous_middle_step = bool(middle_step)
        if m4:
            assert machine.rotors[0].get_position_letter() == "Q"
    assert machine.window() == initial
    assert double_steps == 26


def test_empty_text_does_not_change_state() -> None:
    machine = make_machine(key="ADV")
    assert machine.process_text("") == ""
    assert machine.window() == "ADV"
