"""Enigma machine facade and signal execution."""

from __future__ import annotations

from collections.abc import Sequence

from .alphabet import BASE
from .data import REFLECTORS
from .observer import EnigmaObserver
from .plugboard import Plugboard
from .rotors import Rotor


class EnigmaMachine:
    """Facade that executes Enigma processing."""

    def __init__(
        self,
        rotors: Sequence[Rotor],
        reflector_name: str,
        plugboard: Plugboard,
        greek_rotor: Rotor | None = None,
        observer: EnigmaObserver | None = None,
    ) -> None:
        self.rotors = list(rotors)
        self.reflector_name = reflector_name
        self.plugboard = plugboard
        self.greek_rotor = greek_rotor
        self.observer = observer

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
        index = BASE.index(char)

        for rotor in reversed(self.rotors):
            index = rotor.encode_forward(index)

        if self.greek_rotor is not None:
            index = self.greek_rotor.encode_forward(index)

        index = self._reflect(index)

        if self.greek_rotor is not None:
            index = self.greek_rotor.encode_backward(index)

        for rotor in self.rotors:
            index = rotor.encode_backward(index)

        return self.plugboard.swap(BASE[index])

    def window(self) -> str:
        """Return the current rotor window display."""

        window = "".join(rotor.get_position_letter() for rotor in self.rotors)
        if self.greek_rotor is not None:
            return f"{self.greek_rotor.get_position_letter()} {window}"
        return window

    def _reflect(self, index: int) -> int:
        return BASE.index(REFLECTORS[self.reflector_name][index])

    def _step_rotors(self) -> None:
        left, middle, right = self.rotors
        step_left = middle.at_notch()
        step_middle = middle.at_notch() or right.at_notch()

        right.step()
        if step_middle:
            middle.step()
        if step_left:
            left.step()
