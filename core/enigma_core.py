import string

ALPHABET = string.printable

def encrypt(message, rotors, reflector):
    result = []
    for char in message:
        if char in ALPHABET:
            c = char
            for rotor in rotors:
                c = rotor.encrypt(c)
            c = reflector.reflect(c)
            for rotor in reversed(rotors):
                c = rotor.decrypt(c)
            result.append(c)

            rotate_next = True
            for rotor in rotors:
                if rotate_next:
                    rotate_next = rotor.step()
                else:
                    break
    return ''.join(result)

def decrypt(message, rotors, reflector):
    return encrypt(message, rotors, reflector)
