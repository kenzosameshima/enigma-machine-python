# User interface and interactive CLI for Enigma machine

from engine import (
    enigma_process,
    Rotor,
    parse_key_positions,
    BASE,
)


def prompt_rotor_order():
    print("Available moving rotors: I II III IV V")
    raw = input("Enter rotor order left-to-right (e.g. I II III): ").strip().upper()
    parts = [p for p in raw.replace(",", " ").split() if p]

    if len(parts) != 3:
        return ("I", "II", "III")

    allowed = {"I", "II", "III", "IV", "V"}
    if any(p not in allowed for p in parts):
        return ("I", "II", "III")
    if len(set(parts)) != 3:
        return ("I", "II", "III")

    return tuple(parts)


def prompt_ring_settings(count):
    default = tuple(1 for _ in range(count))
    raw = input(f"Enter {count} ring settings 1-26 (e.g. {' '.join(['1'] * count)}): ").strip()
    parts = [p for p in raw.replace(",", " ").split() if p]
    if len(parts) != count:
        return default

    try:
        values = tuple(int(p) for p in parts)
    except ValueError:
        return default

    if any(v < 1 or v > 26 for v in values):
        return default

    return values


def prompt_plugboard():
    raw = input("Plugboard pairs (e.g. AB CD EF), blank for none: ").strip().upper()
    if not raw:
        return []

    pairs = []
    for token in raw.replace(",", " ").split():
        if len(token) == 2:
            pairs.append((token[0], token[1]))
    return pairs


def display_rotor_window(rotors, greek_rotor=None):
    positions = [r.get_position_letter() for r in rotors]
    window = "".join(positions)
    if greek_rotor:
        window = greek_rotor.get_position_letter() + " " + window
    print(f"\nRotor window: [{window}]")


def daily_key_sheet_mode():
    print("\n=== DAILY KEY SHEET MODE ===")
    print("Simulate a historical Enigma daily key setup.")

    print("\n--- Daily Settings (fixed for all messages that day) ---")

    # Rotor order
    rotor_order = prompt_rotor_order()
    print(f"Rotor order: {' '.join(rotor_order)}")

    # Ring settings
    ring_settings = prompt_ring_settings(3)
    print(f"Ring settings: {' '.join(str(r) for r in ring_settings)}")

    # Reflector
    reflector_name = input("Reflector (B/C, default B): ").strip().upper() or "B"
    if reflector_name not in {"B", "C"}:
        reflector_name = "B"
    print(f"Reflector: {reflector_name}")

    # Plugboard
    plug_pairs = prompt_plugboard()
    if plug_pairs:
        print(f"Plugboard: {' '.join(f'{a}-{b}' for a, b in plug_pairs)}")
    else:
        print("Plugboard: (none)")

    print("\n--- Per-Message Settings (ground setting) ---")
    ground_setting = input("Enter ground setting (3 letters, e.g. AAA): ").strip().upper()
    if len(ground_setting) < 3:
        ground_setting = (ground_setting + "AAA")[:3]
    print(f"Ground setting: {ground_setting}")

    print("\n--- Operator Choice (message key, encrypted) ---")
    message_key_encrypted = input("Enter encrypted message key (3 letters, e.g. QWE): ").strip().upper()
    if len(message_key_encrypted) < 3:
        message_key_encrypted = (message_key_encrypted + "AAA")[:3]

    # First stage: decrypt transmitted message key using daily ground setting.
    message_key = enigma_process(
        message_key_encrypted,
        ground_setting,
        mode="wehrmacht",
        plug_pairs=plug_pairs,
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )
    print(f"Message key decrypted: {message_key}")

    print("\n--- Operator sets initial rotor position to message key ---")
    print(f"Rotors set to: {message_key}")

    # Second stage: encrypt actual message with the recovered message key.
    text = input("\nEnter message to encrypt: ")[:128]
    if not text:
        print("No message entered.")
        return

    encrypted = enigma_process(
        text,
        message_key,
        mode="wehrmacht",
        plug_pairs=plug_pairs,
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )

    print(f"\nPlaintext:  {text}")
    print(f"Ciphertext: {encrypted}")

    # Recipient repeats the same key schedule to recover plaintext.
    print("\n--- Decryption (recipient) ---")
    print(f"Recipient sets rotor to: {message_key}")
    decrypted = enigma_process(
        encrypted,
        message_key,
        mode="wehrmacht",
        plug_pairs=plug_pairs,
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )
    print(f"Decrypted: {decrypted}")


def historical_rotor_constraint(rotor_order, mode):
    """Enforce historical rotor availability constraints."""
    if mode == "m4":
        # M4 always used rotors I-V
        allowed = {"I", "II", "III", "IV", "V"}
        if not all(r in allowed for r in rotor_order):
            print("Warning: M4 used rotors I-V. Reverting to default.")
            return ("I", "II", "III")
    else:
        # Wehrmacht/Naval used rotors I-V
        allowed = {"I", "II", "III", "IV", "V"}
        if not all(r in allowed for r in rotor_order):
            print("Warning: Invalid rotor selection. Reverting to default.")
            return ("I", "II", "III")
    return rotor_order


def main():
    print("=== ENIGMA MACHINE SIMULATOR (A-Z) ===")
    print("0 - Daily Key Sheet (historical simulation)")
    print("1 - Wehrmacht / 3-rotor")
    print("2 - Naval / 3-rotor")
    print("3 - M4 (4th thin rotor + thin reflector)")

    choice = input("\nSelect mode: ").strip()

    if choice == "0":
        daily_key_sheet_mode()
        return

    text = input("\nEnter message (max 128 chars): ")[:128]
    key = input("Enter starting positions (e.g. ABC or ABCD for M4): ")
    if choice == "1":
        mode = "wehrmacht"
        rotor_order = historical_rotor_constraint(prompt_rotor_order(), mode)
        ring_settings = prompt_ring_settings(3)
        reflector_name = input("Reflector (B/C, default B): ").strip().upper() or "B"
        if reflector_name not in {"B", "C"}:
            reflector_name = "B"
        greek_rotor_name = "BETA"
    elif choice == "2":
        mode = "naval"
        rotor_order = historical_rotor_constraint(prompt_rotor_order(), mode)
        ring_settings = prompt_ring_settings(3)
        reflector_name = input("Reflector (B/C, default C): ").strip().upper() or "C"
        if reflector_name not in {"B", "C"}:
            reflector_name = "C"
        greek_rotor_name = "BETA"
    elif choice == "3":
        mode = "m4"
        rotor_order = historical_rotor_constraint(prompt_rotor_order(), mode)
        ring_settings = prompt_ring_settings(4)
        greek_rotor_name = input("Greek rotor (BETA/GAMMA, default BETA): ").strip().upper() or "BETA"
        if greek_rotor_name not in {"BETA", "GAMMA"}:
            greek_rotor_name = "BETA"
        reflector_name = input("Thin reflector (B_THIN/C_THIN, default B_THIN): ").strip().upper() or "B_THIN"
        if reflector_name not in {"B_THIN", "C_THIN"}:
            reflector_name = "B_THIN"
    else:
        print("Invalid choice.")
        return

    plug_pairs = prompt_plugboard()

    # Build rotor objects only for displaying the initial rotor window.
    positions = parse_key_positions(key, 4 if mode == "m4" else 3)
    left_name, middle_name, right_name = rotor_order
    moving_rotors = [
        Rotor(left_name, ring_settings[0], positions[0], can_step=True),
        Rotor(middle_name, ring_settings[1], positions[1], can_step=True),
        Rotor(right_name, ring_settings[2], positions[2], can_step=True),
    ]
    greek_rotor = None
    if mode == "m4":
        greek_rotor = Rotor(greek_rotor_name, ring_settings[3], positions[3], can_step=False)

    display_rotor_window(moving_rotors, greek_rotor)

    encrypted = enigma_process(
        text,
        key,
        mode=mode,
        plug_pairs=plug_pairs,
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        reflector_name=reflector_name,
        greek_rotor_name=greek_rotor_name,
    )
    decrypted = enigma_process(
        encrypted,
        key,
        mode=mode,
        plug_pairs=plug_pairs,
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        reflector_name=reflector_name,
        greek_rotor_name=greek_rotor_name,
    )

    print(f"\nEncrypted:  {encrypted}")
    print(f"Decrypted:  {decrypted}")


if __name__ == "__main__":
    main()
