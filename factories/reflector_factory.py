from core.reflector import Reflector, ALPHABET

class ReflectorFactory:
    def __init__(self, alphabet=ALPHABET):
        print("Initializing Reflectors...")
        self.alphabet = alphabet

    def create_reflector(self, seed=0):
        return Reflector(seed=seed, alphabet=self.alphabet)
