from utils.utils import get_int_input, initialize_components, format_color, GREEN, CYAN
from core.enigma_core import encrypt, decrypt

if __name__ == "__main__":
    message = input("Enter a message to encrypt: ")
    rotor_offsets = [get_int_input(f"Offset for rotor {i+1}: ") for i in range(3)]
    seed = get_int_input("Reflector seed: ")

    rotors, reflector = initialize_components(rotor_offsets, seed)

    encrypted = encrypt(message, rotors, reflector)
    print(format_color(f"Encrypted: {encrypted}", GREEN))

    rotors, reflector = initialize_components(rotor_offsets, seed)
    decrypted = decrypt(encrypted, rotors, reflector)
    print(format_color(f"Decrypted: {decrypted}", CYAN))
