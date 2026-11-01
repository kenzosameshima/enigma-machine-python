"""Factory for constructing Enigma machine instances."""

from __future__ import annotations

from .alphabet import letter_to_index
from .config import EnigmaConfig
from .data import ROTOR_SPECS
from .machine import EnigmaMachine
from .modes import MODE_SPECS
from .plugboard import Plugboard
from .rotors import Rotor, RotorState


class EnigmaFactory:
    """Centralized Enigma machine construction."""

    def create(self, config: EnigmaConfig) -> EnigmaMachine:
        """Return a fresh machine with isolated rotor state.

        config is already validated: EnigmaConfig.__post_init__ validates
        every field, including mode-specific sizing and reflector rules, on
        construction.
        """

        if MODE_SPECS[config.mode].requires_greek:
            return self._create_m4(config)
        return self._create_three_rotor(config)

    def _create_three_rotor(self, config: EnigmaConfig) -> EnigmaMachine:
        return EnigmaMachine(
            rotors=self._create_moving_rotors(config),
            reflector_name=config.reflector_name,
            plugboard=Plugboard(config.plugboard_pairs),
        )

    def _create_m4(self, config: EnigmaConfig) -> EnigmaMachine:
        return EnigmaMachine(
            rotors=self._create_moving_rotors(config),
            reflector_name=config.reflector_name,
            plugboard=Plugboard(config.plugboard_pairs),
            greek_rotor=self._create_greek_rotor(config),
        )

    @staticmethod
    def _create_moving_rotors(config: EnigmaConfig) -> list[Rotor]:
        return [
            Rotor(
                ROTOR_SPECS[name],
                RotorState(ring=ring - 1, position=letter_to_index(position)),
            )
            for name, ring, position in zip(
                config.rotor_order,
                config.ring_settings[:3],
                config.positions[:3],
                strict=True,
            )
        ]

    @staticmethod
    def _create_greek_rotor(config: EnigmaConfig) -> Rotor:
        return Rotor(
            ROTOR_SPECS[config.greek_rotor],
            RotorState(
                ring=config.ring_settings[3] - 1,
                position=letter_to_index(config.positions[3]),
            ),
            can_step=False,
        )
