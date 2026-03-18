# Core Enigma machine logic (no I/O)

from config import ROTOR_SPECS, REFLECTORS

BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Rotor:
    def __init__(self, name, ring_setting=1, position="A", can_step=True):
        spec = ROTOR_SPECS[name]
        self.name = name
        # Convert letter wiring to index wiring for fast arithmetic operations.
        self.wiring = [BASE.index(c) for c in spec["wiring"]]
        self.inverse_wiring = [0] * 26

        for i, mapped in enumerate(self.wiring):
            self.inverse_wiring[mapped] = i

        # Some rotors (Beta/Gamma) have no notch and do not trigger turnover.
        self.notches = [BASE.index(c) for c in spec["notch"]]
        self.ring = ring_setting - 1
        self.position = BASE.index(position)
        self.can_step = can_step

    def at_notch(self):
        # Ring setting shifts the turnover letter relative to the window position.
        return (self.position + self.ring) % 26 in self.notches

    def get_position_letter(self):
        return BASE[self.position]

    def step(self):
        if self.can_step:
            self.position = (self.position + 1) % 26

    def encode_forward(self, index):
        # Apply rotor position/ring offset, pass through wiring, then unshift.
        shifted = (index + self.position - self.ring) % 26
        wired = self.wiring[shifted]
        return (wired - self.position + self.ring) % 26

    def encode_backward(self, index):
        shifted = (index + self.position - self.ring) % 26
        wired = self.inverse_wiring[shifted]
        return (wired - self.position + self.ring) % 26


def plugboard_swap(char, pairs):
    for a, b in pairs:
        if char == a:
            return b
        if char == b:
            return a
    return char


def normalize_pairs(pairs):
    normalized = []
    used = set()
    invalid = []

    for a, b in pairs:
        a = a.upper()
        b = b.upper()
        if a == b:
            invalid.append((a, b, "same letter"))
            continue
        if a not in BASE or b not in BASE:
            invalid.append((a, b, "invalid characters"))
            continue
        if a in used or b in used:
            invalid.append((a, b, "letter already used"))
            continue
        normalized.append((a, b))
        used.add(a)
        used.add(b)

    if invalid:
        print(f"Warning: {len(invalid)} plugboard pair(s) discarded:")
        for a, b, reason in invalid:
            print(f"  {a}-{b}: {reason}")

    # Historical plugboard limit: up to 10 cable pairs.
    return normalized[:10]


def reflector(index, reflector_name):
    return BASE.index(REFLECTORS[reflector_name][index])


def parse_key_positions(key, rotor_count):
    # Keep only valid letters and pad with A for missing positions.
    key = "".join(ch for ch in key.upper() if ch in BASE)
    if len(key) < rotor_count:
        key = (key + ("A" * rotor_count))[:rotor_count]
    return key[:rotor_count]


def step_rotors(rotors):
    left, middle, right = rotors
    # Evaluate notch states before stepping to reproduce double-stepping behavior.
    step_left = middle.at_notch()
    step_middle = middle.at_notch() or right.at_notch()

    right.step()
    if step_middle:
        middle.step()
    if step_left:
        left.step()


def process_char(char, moving_rotors, reflector_name, greek_rotor=None, plug_pairs=None):
    if plug_pairs is None:
        plug_pairs = []

    # ETW is modeled as identity (A->A ... Z->Z), so no explicit transform here.
    char = plugboard_swap(char, plug_pairs)
    index = BASE.index(char)

    # Right -> left through moving rotors.
    for rotor in reversed(moving_rotors):
        index = rotor.encode_forward(index)

    # M4 inserts the non-stepping Greek rotor between left rotor and reflector.
    if greek_rotor is not None:
        index = greek_rotor.encode_forward(index)

    index = reflector(index, reflector_name)

    if greek_rotor is not None:
        index = greek_rotor.encode_backward(index)

    # Left -> right returning from reflector.
    for rotor in moving_rotors:
        index = rotor.encode_backward(index)

    char = BASE[index]
    return plugboard_swap(char, plug_pairs)


def enigma_process(
    text,
    key,
    mode="wehrmacht",
    plug_pairs=None,
    rotor_order=("I", "II", "III"),
    ring_settings=(1, 1, 1),
    reflector_name="B",
    greek_rotor_name="BETA",
):
    if plug_pairs is None:
        plug_pairs = []

    text = text.upper()
    plug_pairs = normalize_pairs(plug_pairs)

    if mode not in {"wehrmacht", "naval", "m4"}:
        raise ValueError("Invalid mode")

    # Enforce machine-specific configuration constraints.
    if mode == "m4":
        if len(rotor_order) != 3 or len(ring_settings) != 4:
            raise ValueError("M4 requires 3 moving rotors and 4 ring settings")
        if reflector_name not in {"B_THIN", "C_THIN"}:
            raise ValueError("M4 uses thin reflectors: B_THIN or C_THIN")
    else:
        if len(rotor_order) != 3 or len(ring_settings) != 3:
            raise ValueError("3-rotor mode requires 3 rotor names and 3 ring settings")
        if reflector_name not in {"B", "C"}:
            raise ValueError("3-rotor mode uses reflector B or C")

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

    result = []
    for char in text:
        if char not in BASE:
            result.append(char)
            continue

        # Rotor stepping occurs before signal encoding on each keypress.
        step_rotors(moving_rotors)
        enc = process_char(char, moving_rotors, reflector_name, greek_rotor, plug_pairs)
        result.append(enc)

    return "".join(result)
