"""Interactive command-line interface for the Enigma machine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from .alphabet import BASE
from .config import EnigmaConfig, EnigmaConfigBuilder
from .factory import EnigmaFactory
from .modes import MachineModeName, ReflectorName

MAX_MESSAGE_LENGTH = 128
DEFAULT_ROTOR_ORDER = ("I", "II", "III")
MOVING_ROTORS = {"I", "II", "III", "IV", "V"}


def prompt_rotor_order() -> tuple[str, str, str]:
    print("Available moving rotors: I II III IV V")
    raw = input("Enter rotor order left-to-right (e.g. I II III): ").strip().upper()
    parts = tuple(part for part in raw.replace(",", " ").split() if part)

    if len(parts) != 3:
        return DEFAULT_ROTOR_ORDER
    if any(part not in MOVING_ROTORS for part in parts):
        return DEFAULT_ROTOR_ORDER
    if len(set(parts)) != 3:
        return DEFAULT_ROTOR_ORDER
    return parts


def prompt_ring_settings(count: int) -> tuple[int, ...]:
    default = tuple(1 for _ in range(count))
    example = " ".join(["1"] * count)
    raw = input(f"Enter {count} ring settings 1-26 (e.g. {example}): ").strip()
    parts = tuple(part for part in raw.replace(",", " ").split() if part)
    if len(parts) != count:
        return default

    try:
        values = tuple(int(part) for part in parts)
    except ValueError:
        return default

    if any(value < 1 or value > 26 for value in values):
        return default
    return values


def prompt_plugboard() -> list[tuple[str, str]]:
    raw = input("Plugboard pairs (e.g. AB CD EF), blank for none: ").strip().upper()
    if not raw:
        return []

    pairs = []
    for token in raw.replace(",", " ").split():
        if len(token) == 2 and token[0] in BASE and token[1] in BASE:
            pairs.append((token[0], token[1]))
    return pairs


def prompt_reflector(
    prompt: str,
    default: ReflectorName,
    allowed: set[ReflectorName],
) -> str:
    raw = input(prompt).strip().upper()
    reflector = raw or default.value
    if reflector not in {item.value for item in allowed}:
        return default.value
    return reflector


def prompt_greek_rotor() -> str:
    raw = input("Greek rotor (BETA/GAMMA, default BETA): ").strip().upper()
    if raw in {"BETA", "GAMMA"}:
        return raw
    return "BETA"


def process_config(config: EnigmaConfig) -> tuple[str, str]:
    machine = EnigmaFactory().create(config)
    window = machine.window()
    output = machine.process_text(config.text)
    return window, output


class CliCommand(ABC):
    """Command pattern base class for CLI actions."""

    @abstractmethod
    def execute(self) -> str:
        """Collect input, run a machine, and return display text."""

    def _build_config(
        self,
        text: str,
        key: str,
        mode: MachineModeName,
        rotor_order: Sequence[str],
        ring_settings: Sequence[int],
        reflector_name: str,
        plug_pairs: Sequence[tuple[str, str]],
        greek_rotor_name: str = "BETA",
    ) -> EnigmaConfig:
        return (
            EnigmaConfigBuilder()
            .text(text)
            .mode(mode)
            .rotors(rotor_order)
            .rings(ring_settings)
            .key(key)
            .reflector(reflector_name)
            .plugboard(plug_pairs)
            .greek(greek_rotor_name)
            .build()
        )


class ThreeRotorCommand(CliCommand):
    """CLI command for Wehrmacht/Naval three-rotor modes."""

    def __init__(
        self,
        mode: MachineModeName,
        default_reflector: ReflectorName,
    ) -> None:
        self.mode = mode
        self.default_reflector = default_reflector

    def execute(self) -> str:
        text = input("\nEnter message (max 128 chars): ")[:MAX_MESSAGE_LENGTH]
        key = input("Enter starting positions (e.g. ABC): ")
        rotor_order = prompt_rotor_order()
        ring_settings = prompt_ring_settings(3)
        reflector_name = prompt_reflector(
            f"Reflector (B/C, default {self.default_reflector.value}): ",
            self.default_reflector,
            {ReflectorName.B, ReflectorName.C},
        )
        plug_pairs = prompt_plugboard()

        config = self._build_config(
            text=text,
            key=key,
            mode=self.mode,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
        )
        window, encrypted = process_config(config)
        decrypt_config = self._build_config(
            text=encrypted,
            key=key,
            mode=self.mode,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
        )
        _, decrypted = process_config(decrypt_config)
        return (
            f"\nRotor window: [{window}]\n"
            f"Encrypted:  {encrypted}\n"
            f"Decrypted:  {decrypted}"
        )


class M4Command(CliCommand):
    """CLI command for the four-rotor M4 mode."""

    def execute(self) -> str:
        text = input("\nEnter message (max 128 chars): ")[:MAX_MESSAGE_LENGTH]
        key = input("Enter starting positions (e.g. ABCD): ")
        rotor_order = prompt_rotor_order()
        ring_settings = prompt_ring_settings(4)
        greek_rotor_name = prompt_greek_rotor()
        reflector_name = prompt_reflector(
            "Thin reflector (B_THIN/C_THIN, default B_THIN): ",
            ReflectorName.B_THIN,
            {ReflectorName.B_THIN, ReflectorName.C_THIN},
        )
        plug_pairs = prompt_plugboard()

        config = self._build_config(
            text=text,
            key=key,
            mode=MachineModeName.M4,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
            greek_rotor_name=greek_rotor_name,
        )
        window, encrypted = process_config(config)
        decrypt_config = self._build_config(
            text=encrypted,
            key=key,
            mode=MachineModeName.M4,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
            greek_rotor_name=greek_rotor_name,
        )
        _, decrypted = process_config(decrypt_config)
        return (
            f"\nRotor window: [{window}]\n"
            f"Encrypted:  {encrypted}\n"
            f"Decrypted:  {decrypted}"
        )


class DailyKeySheetCommand(CliCommand):
    """CLI command for historical daily key sheet simulation."""

    def execute(self) -> str:
        print("\n=== DAILY KEY SHEET MODE ===")
        print("Simulate a historical Enigma daily key setup.")
        print("\n--- Daily Settings (fixed for all messages that day) ---")

        rotor_order = prompt_rotor_order()
        ring_settings = prompt_ring_settings(3)
        reflector_name = prompt_reflector(
            "Reflector (B/C, default B): ",
            ReflectorName.B,
            {ReflectorName.B, ReflectorName.C},
        )
        plug_pairs = prompt_plugboard()

        print("\n--- Per-Message Settings (ground setting) ---")
        ground_setting = input("Enter ground setting (3 letters, e.g. AAA): ")

        print("\n--- Operator Choice (message key, encrypted) ---")
        message_key_encrypted = input(
            "Enter encrypted message key (3 letters, e.g. QWE): "
        )

        key_config = self._build_config(
            text=message_key_encrypted,
            key=ground_setting,
            mode=MachineModeName.WEHRMACHT,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
        )
        _, message_key = process_config(key_config)

        text = input("\nEnter message to encrypt: ")[:MAX_MESSAGE_LENGTH]
        if not text:
            return "No message entered."

        encrypt_config = self._build_config(
            text=text,
            key=message_key,
            mode=MachineModeName.WEHRMACHT,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
        )
        _, encrypted = process_config(encrypt_config)

        decrypt_config = self._build_config(
            text=encrypted,
            key=message_key,
            mode=MachineModeName.WEHRMACHT,
            rotor_order=rotor_order,
            ring_settings=ring_settings,
            reflector_name=reflector_name,
            plug_pairs=plug_pairs,
        )
        _, decrypted = process_config(decrypt_config)

        return (
            f"Rotor order: {' '.join(rotor_order)}\n"
            f"Ring settings: {' '.join(str(item) for item in ring_settings)}\n"
            f"Reflector: {reflector_name}\n"
            f"Message key decrypted: {message_key}\n"
            f"Plaintext:  {text}\n"
            f"Ciphertext: {encrypted}\n"
            f"Decrypted: {decrypted}"
        )


def main() -> None:
    print("=== ENIGMA MACHINE SIMULATOR (A-Z) ===")
    print("0 - Daily Key Sheet (historical simulation)")
    print("1 - Wehrmacht / 3-rotor")
    print("2 - Naval / 3-rotor")
    print("3 - M4 (4th thin rotor + thin reflector)")

    commands: dict[str, CliCommand] = {
        "0": DailyKeySheetCommand(),
        "1": ThreeRotorCommand(MachineModeName.WEHRMACHT, ReflectorName.B),
        "2": ThreeRotorCommand(MachineModeName.NAVAL, ReflectorName.C),
        "3": M4Command(),
    }

    choice = input("\nSelect mode: ").strip()
    command = commands.get(choice)
    if command is None:
        print("Invalid choice.")
        return

    try:
        print(command.execute())
    except ValueError as exc:
        print(f"Configuration error: {exc}")


if __name__ == "__main__":
    main()
