"""Independent contact-pair model; never imports the package under test.

Wiring and window turnover letters transcribed from Crypto Museum:
https://www.cryptomuseum.com/crypto/enigma/wiring.htm (Enigma I, M3, M4).
Stepping follows the pawl description and double-step sequence at:
https://kerryb.github.io/enigma/#rotor-advance

Unlike the production index/inverse-array implementation, this model rebuilds
physical contact-pair dictionaries and reverses their pairs for the return path.
All orders, positions and rings here are physical left-to-right (Greek FIRST).
This is a differential oracle, not a historical message vector.
"""

from string import ascii_uppercase

WIRING = {
    "I": "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II": "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV": "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V": "VZBRGITYUPSDNHLXAWMJQOFECK",
    "BETA": "LEYJVCNIXWPBQMDRTAKZGFUHOS",
    "GAMMA": "FSOKANUERHMBTIYCWLQPZXVGJD",
}
TURNOVER = {"I": "Q", "II": "E", "III": "V", "IV": "J", "V": "Z"}
REFLECTION = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
    "B_THIN": "ENKQAUYWJICOPBLMDXZVFTHRGS",
    "C_THIN": "RDOBJNTKVEHMLFCWZAXGYIPSUQ",
}


def contacts(name: str, window: str, ring: int) -> dict[str, str]:
    labels = ascii_uppercase
    rotation = (ring - 1 - labels.index(window)) % 26
    rotated = labels[rotation:] + labels[:rotation]
    return {
        rotated[pin]: rotated[labels.index(wire)]
        for pin, wire in enumerate(WIRING[name])
    }


def advance(order: tuple[str, ...], windows: list[str]) -> None:
    moving = {len(order) - 1}
    # Each engaged pawl moves both wheels alongside it, simultaneously.
    for index in (len(order) - 1, len(order) - 2):
        if windows[index] == TURNOVER[order[index]]:
            moving.update((index, index - 1))
    for index in moving:
        windows[index] = ascii_uppercase[
            (ascii_uppercase.index(windows[index]) + 1) % 26
        ]


def reference_process(  # noqa: PLR0913 -- explicit independent machine settings
    text: str,
    *,
    order: tuple[str, ...],
    windows: str,
    rings: tuple[int, ...],
    reflector: str,
    pairs: tuple[tuple[str, str], ...] = (),
) -> str:
    positions = list(windows)
    plugs = dict(pairs)
    plugs.update((b, a) for a, b in pairs)
    reflection = dict(zip(ascii_uppercase, REFLECTION[reflector], strict=True))
    result = []
    for original in text:
        char = (
            original.upper() if original in "abcdefghijklmnopqrstuvwxyz" else original
        )
        if char not in ascii_uppercase:
            result.append(original)
            continue
        advance(order, positions)
        maps = [
            contacts(name, position, ring)
            for name, position, ring in zip(order, positions, rings, strict=True)
        ]
        char = plugs.get(char, char)
        for mapping in reversed(maps):
            char = mapping[char]
        char = reflection[char]
        for mapping in maps:
            char = {b: a for a, b in mapping.items()}[char]
        result.append(plugs.get(char, char))
    return "".join(result)
