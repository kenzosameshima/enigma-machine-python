"""Enigma machine facade and signal execution."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import (
    BASE,
    GREEK_ROTORS,
    ascii_upper,
    index_to_letter,
    letter_to_index,
    validate_moving_rotor_names,
)
from .config import EnigmaConfig
from .data import REFLECTORS, ROTOR_SPECS
from .modes import MODE_SPECS
from .plugboard import Plugboard
from .rotors import Rotor, RotorState


class EnigmaMachine:
    """Executable Enigma machine with mutable rotor positions.

    Construction always clones the rotors passed in, so separate machines
    never share stepping state, even when built from the same Rotor objects.

    self.rotors holds every rotor in physical, reflector-to-keyboard order:
    [greek, left, middle, right] for M4, or [left, middle, right] otherwise.
    That ordering lets encode_signal traverse it uniformly in both
    directions; stepping and the window display still only care about the
    three moving rotors, which are always its last three elements.
    """

    def __init__(
        self,
        rotors: Sequence[Rotor],
        reflector_name: str,
        plugboard: Plugboard,
        greek_rotor: Rotor | None = None,
    ) -> None:
        self._validate_configuration(rotors, reflector_name, plugboard, greek_rotor)
        greek = [greek_rotor.clone()] if greek_rotor is not None else []
        self.rotors = greek + [rotor.clone() for rotor in rotors]
        self.reflector_name = reflector_name
        self.plugboard = plugboard
        self._initial_rotor_states = tuple(rotor.snapshot() for rotor in self.rotors)

    @classmethod
    def from_config(cls, config: EnigmaConfig) -> EnigmaMachine:
        """Build a fresh machine from an already-validated configuration."""

        moving_rotors = [
            Rotor(
                ROTOR_SPECS[name],
                RotorState(ring=ring - 1, position=letter_to_index(position)),
            )
            for name, ring, position in zip(
                config.rotor_order,
                config.ring_settings[:3],
                config.key[:3],
                strict=True,
            )
        ]
        greek_rotor = None
        if MODE_SPECS[config.mode].requires_greek:
            greek_rotor = Rotor(
                ROTOR_SPECS[config.greek_rotor_name],
                RotorState(
                    ring=config.ring_settings[3] - 1,
                    position=letter_to_index(config.key[3]),
                ),
                can_step=False,
            )
        return cls(
            rotors=moving_rotors,
            reflector_name=config.reflector_name,
            plugboard=Plugboard(config.plugboard_pairs),
            greek_rotor=greek_rotor,
        )

    def reset(self) -> None:
        """Restore the rotor windows and rings captured at construction time."""

        for rotor, state in zip(self.rotors, self._initial_rotor_states, strict=True):
            rotor.restore(state)

    def process_text(self, text: str) -> str:
        """Process every character in text."""

        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        return "".join(self.process_char(char) for char in text)

    def process_char(self, char: str) -> str:
        """Normalize ASCII letters and preserve every other single character."""

        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("Character must be a single character")
        char = ascii_upper(char)
        if char not in BASE:
            return char

        self.step_rotors()
        return self.encode_signal(char)

    def encode_signal(self, char: str) -> str:
        """Encode one alphabetic character without stepping rotors."""

        char = self.plugboard.swap(char)
        index = letter_to_index(char)

        for rotor in reversed(self.rotors):
            index = rotor.encode_forward(index)

        index = self._reflect(index)

        for rotor in self.rotors:
            index = rotor.encode_backward(index)

        return self.plugboard.swap(index_to_letter(index))

    def window(self) -> str:
        """Return the current rotor window display, Greek rotor last (matches key())."""

        if len(self.rotors) == 4:
            greek, *moving = self.rotors
            letters = "".join(rotor.get_position_letter() for rotor in moving)
            return f"{letters} {greek.get_position_letter()}"
        return "".join(rotor.get_position_letter() for rotor in self.rotors)

    def _reflect(self, index: int) -> int:
        return letter_to_index(REFLECTORS[self.reflector_name][index])

    def step_rotors(self) -> None:
        """Advance the moving rotors by one keystroke without encoding a character."""

        left, middle, right = self.rotors[-3:]
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
        validate_moving_rotor_names([rotor.name for rotor in rotors])
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
