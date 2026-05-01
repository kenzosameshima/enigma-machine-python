"""Observer extension point for tracing machine execution."""

from abc import ABC, abstractmethod


class EnigmaObserver(ABC):
    """Optional observer for debug or tracing output."""

    @abstractmethod
    def on_rotor_step(self, window: str) -> None:
        """Called after rotors step."""

    @abstractmethod
    def on_char_processed(self, input_char: str, output_char: str) -> None:
        """Called after an alphabetic character is processed."""
