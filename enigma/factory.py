"""Factory for constructing Enigma machine instances."""

from __future__ import annotations

from .alphabet import BASE
from .config import EnigmaConfig
from .data import ROTOR_SPECS
from .machine import EnigmaMachine
from .observer import EnigmaObserver
from .plugboard import Plugboard
from .rotors import Rotor, RotorState


class EnigmaFactory:
    """Centralized Enigma machine construction."""

    def create(
        self,
        config: EnigmaConfig,
        observer: EnigmaObserver | None = None,
    ) -> EnigmaMachine:
        config.mode_strategy.validate(config)
        creators = {
            3: self._create_three_rotor,
            4: self._create_m4,
        }
        return creators[config.mode_strategy.rotor_count()](config, observer)

    def _create_three_rotor(
        self,
        config: EnigmaConfig,
        observer: EnigmaObserver | None = None,
    ) -> EnigmaMachine:
        return EnigmaMachine(
            rotors=self._create_moving_rotors(config),
            reflector_name=config.reflector_name,
            plugboard=Plugboard(config.plugboard_pairs),
            observer=observer,
        )

    def _create_m4(
        self,
        config: EnigmaConfig,
        observer: EnigmaObserver | None = None,
    ) -> EnigmaMachine:
        return EnigmaMachine(
            rotors=self._create_moving_rotors(config),
            reflector_name=config.reflector_name,
            plugboard=Plugboard(config.plugboard_pairs),
            greek_rotor=self._create_greek_rotor(config),
            observer=observer,
        )

    @staticmethod
    def _create_moving_rotors(config: EnigmaConfig) -> list[Rotor]:
        return [
            Rotor(
                ROTOR_SPECS[name],
                RotorState(ring=ring - 1, position=BASE.index(position)),
            )
            for name, ring, position in zip(
                config.rotor_order,
                config.ring_settings[:3],
                config.positions[:3],
            )
        ]

    @staticmethod
    def _create_greek_rotor(config: EnigmaConfig) -> Rotor:
        return Rotor(
            ROTOR_SPECS[config.greek_rotor],
            RotorState(
                ring=config.ring_settings[3] - 1,
                position=BASE.index(config.positions[3]),
            ),
            can_step=False,
        )
