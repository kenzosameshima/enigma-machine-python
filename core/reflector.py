import string

ALPHABET = string.printable

class Reflector:
    def __init__(self, seed=0, alphabet=ALPHABET):
        self.alphabet = list(alphabet)
        assert len(self.alphabet) % 2 == 0
        self.mapping = {}

        indices = self._pseudo_shuffle(range(len(self.alphabet)), seed)

        for i in range(0, len(self.alphabet), 2):
            a = self.alphabet[indices[i]]
            b = self.alphabet[indices[i + 1]]
            self.mapping[a] = b
            self.mapping[b] = a

    def _pseudo_shuffle(self, items, seed):
        shuffled = list(items)
        n = len(shuffled)

        a = 1103515245
        c = 12345
        m = 2**31
        state = seed

        for i in range(n - 1, 0, -1):
            state = (a * state + c) % m
            j = state % (i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        return shuffled

    def reflect(self, char):
        return self.mapping.get(char, char)
