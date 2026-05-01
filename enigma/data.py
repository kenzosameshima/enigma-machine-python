"""Static rotor and reflector data."""

from .modes import ReflectorName
from .rotors import RotorSpec

ROTOR_SPECS = {
    "I": RotorSpec("I", "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II": RotorSpec("II", "AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": RotorSpec("III", "BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV": RotorSpec("IV", "ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V": RotorSpec("V", "VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
    "BETA": RotorSpec("BETA", "LEYJVCNIXWPBQMDRTAKZGFUHOS", ""),
    "GAMMA": RotorSpec("GAMMA", "FSOKANUERHMBTIYCWLQPZXVGJD", ""),
}

REFLECTORS = {
    ReflectorName.B.value: "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    ReflectorName.C.value: "FVPJIAOYEDRZXWGCTKUQSBNMHL",
    ReflectorName.B_THIN.value: "ENKQAUYWJICOPBLMDXZVFTHRGS",
    ReflectorName.C_THIN.value: "RDOBJNTKVEHMLFCWZAXGYIPSUQ",
}
