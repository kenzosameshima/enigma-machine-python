import string

ALPHABET = string.printable

class Rotor:
    def __init__(self, offset=0, alphabet=ALPHABET):
        self.alphabet = alphabet
        self.size = len(alphabet)
        self.offset = offset % self.size
        self._char_to_index = {char: i for i, char in enumerate(alphabet)}
        self._update_rotor()

    def _update_rotor(self):
        self.mapping = [self.alphabet[(i + self.offset) % self.size] for i in range(self.size)]
        self.reverse_mapping = {char: i for i, char in enumerate(self.mapping)}

    def step(self):
        self.offset = (self.offset + 1) % self.size
        self._update_rotor()
        return self.offset == 0 

    def encrypt(self, char):
        if char not in self._char_to_index:
            raise ValueError(f"Character '{char}' not in rotor alphabet.")
        index = self._char_to_index[char]
        return self.mapping[index]

    def decrypt(self, char):
        if char not in self.reverse_mapping:
            raise ValueError(f"Character '{char}' not in rotor mapping.")
        index = self.reverse_mapping[char]
        return self.alphabet[index]
