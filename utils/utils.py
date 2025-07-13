from factories.rotor_factory import RotorFactory
from factories.reflector_factory import ReflectorFactory

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"

def format_color(text, color):
    return f"{color}{text}{RESET}"

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print(format_color("Please enter a valid integer.", RED))

def initialize_components(offsets, seed):
    rotor_factory = RotorFactory()
    reflector_factory = ReflectorFactory()

    rotors = rotor_factory.create_rotor_sequence(offsets)
    reflector = reflector_factory.create_reflector(seed)

    return rotors, reflector
