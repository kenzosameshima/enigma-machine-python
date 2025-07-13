from core.rotor import Rotor, ALPHABET

class RotorFactory:
    def __init__(self, alphabet=ALPHABET):
        print("Initializing Rotors...")
        self.alphabet = alphabet
        self.size = len(alphabet)

    def create_rotor(self, offset=0):
        return Rotor(offset=offset, alphabet=self.alphabet)

    def create_rotor_sequence(self, offsets):
        return [self.create_rotor(offset) for offset in offsets]
