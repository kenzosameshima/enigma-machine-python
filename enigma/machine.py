"""Enigma machine facade and signal execution."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import (
    BASE,
    GREEK_ROTORS,
    MOVING_ROTORS,
    index_to_letter,
    letter_to_index,
)
from .data import REFLECTORS
from .observer import EnigmaObserver
from .plugboard import Plugboard
from .rotors import Rotor, RotorState


class EnigmaMachine:
    """Facade that executes Enigma processing."""

    def __init__(
        self,
        rotors: Sequence[Rotor],
        reflector_name: str,
        plugboard: Plugboard,
        greek_rotor: Rotor | None = None,
        observer: EnigmaObserver | None = None,
        *,
        copy_rotors: bool = True,
    ) -> None:
        self._validate_configuration(rotors, reflector_name, plugboard, greek_rotor)
        self.rotors = (
            [_clone_rotor(rotor) for rotor in rotors]
            if copy_rotors
            else list(rotors)
        )
        self.reflector_name = reflector_name
        self.plugboard = plugboard
        self.greek_rotor = (
            _clone_rotor(greek_rotor)
            if copy_rotors and greek_rotor is not None
            else greek_rotor
        )
        self.observer = observer
        self._initial_rotor_states = _snapshot_rotors(self.rotors)
        self._initial_greek_rotor_state = (
            _snapshot_rotor(self.greek_rotor) if self.greek_rotor is not None else None
        )

    def reset(self) -> None:
        """Restore the rotor windows and rings captured at construction time."""

        _restore_rotors(self.rotors, self._initial_rotor_states)
        if self.greek_rotor is not None and self._initial_greek_rotor_state is not None:
            _restore_rotor(self.greek_rotor, self._initial_greek_rotor_state)

    def process_text(self, text: str) -> str:
        """Process every character in text."""

        return "".join(self.process_char(char) for char in text.upper())

    def process_char(self, char: str) -> str:
        """Process a single character, preserving non-A-Z characters."""

        if char not in BASE:
            return char

        input_char = char
        self._step_rotors()
        if self.observer:
            self.observer.on_rotor_step(self.window())

        output_char = self.encode_signal(char)
        if self.observer:
            self.observer.on_char_processed(input_char, output_char)
        return output_char

    def encode_signal(self, char: str) -> str:
        """Encode one alphabetic character without stepping rotors."""

        char = self.plugboard.swap(char)
        index = letter_to_index(char)

        for rotor in reversed(self.rotors):
            index = rotor.encode_forward(index)

        if self.greek_rotor is not None:
            index = self.greek_rotor.encode_forward(index)

        index = self._reflect(index)

        if self.greek_rotor is not None:
            index = self.greek_rotor.encode_backward(index)

        for rotor in self.rotors:
            index = rotor.encode_backward(index)

        return self.plugboard.swap(index_to_letter(index))

    def window(self) -> str:
        """Return the current rotor window display."""

        window = "".join(rotor.get_position_letter() for rotor in self.rotors)
        if self.greek_rotor is not None:
            return f"{self.greek_rotor.get_position_letter()} {window}"
        return window

    def _reflect(self, index: int) -> int:
        return letter_to_index(REFLECTORS[self.reflector_name][index])

    def _step_rotors(self) -> None:
        left, middle, right = self.rotors
        step_left, step_middle, step_right = _should_step_rotors(
            middle_at_notch=middle.at_notch(),
            right_at_notch=right.at_notch(),
        )

        # The right rotor advances before every alphabetic character.
        if step_right:
            right.step()
        # The middle rotor advances when the right rotor reaches turnover,
        # and also during the classic double-step when the middle is at notch.
        if step_middle:
            middle.step()
        # The left rotor advances only when the middle rotor is at turnover.
        if step_left:
            left.step()

    @staticmethod
    def _validate_configuration(
        rotors: Sequence[Rotor],
        reflector_name: str,
        plugboard: Plugboard,
        greek_rotor: Rotor | None,
    ) -> None:
        if len(rotors) != 3:
            raise ValueError("EnigmaMachine requires exactly 3 moving rotors")
        if not all(isinstance(rotor, Rotor) for rotor in rotors):
            raise TypeError("EnigmaMachine rotors must be Rotor instances")
        if any(not rotor.can_step for rotor in rotors):
            raise ValueError("Moving rotors must be able to step")
        if any(rotor.name not in MOVING_ROTORS for rotor in rotors):
            raise ValueError("Moving rotors must be selected from I, II, III, IV, V")
        if len({rotor.name for rotor in rotors}) != len(rotors):
            raise ValueError("Moving rotors must be unique")
        if reflector_name not in REFLECTORS:
            raise ValueError(f"Unknown reflector: {reflector_name}")
        if not isinstance(plugboard, Plugboard):
            raise TypeError("EnigmaMachine plugboard must be a Plugboard instance")
        if greek_rotor is None:
            return
        if not isinstance(greek_rotor, Rotor):
            raise TypeError("Greek rotor must be a Rotor instance")
        if greek_rotor.name not in GREEK_ROTORS:
            raise ValueError("Greek rotor must be BETA or GAMMA")
        if greek_rotor.can_step:
            raise ValueError("Greek rotor must not step")


def _should_step_rotors(
    *,
    middle_at_notch: bool,
    right_at_notch: bool,
) -> tuple[bool, bool, bool]:
    """Return left, middle, right stepping decisions for three moving rotors."""

    step_left = middle_at_notch
    step_middle = middle_at_notch or right_at_notch
    step_right = True
    return step_left, step_middle, step_right


def _clone_rotor(rotor: Rotor) -> Rotor:
    return Rotor(
        rotor.spec,
        RotorState(ring=rotor.ring, position=rotor.position),
        can_step=rotor.can_step,
    )


def _snapshot_rotors(rotors: Sequence[Rotor]) -> tuple[tuple[int, int], ...]:
    return tuple(_snapshot_rotor(rotor) for rotor in rotors)


def _snapshot_rotor(rotor: Rotor) -> tuple[int, int]:
    return rotor.ring, rotor.position


def _restore_rotors(
    rotors: Sequence[Rotor],
    states: Sequence[tuple[int, int]],
) -> None:
    for rotor, state in zip(rotors, states, strict=True):
        _restore_rotor(rotor, state)


def _restore_rotor(rotor: Rotor, state: tuple[int, int]) -> None:
    ring, position = state
    rotor.state = RotorState(ring=ring, position=position)
