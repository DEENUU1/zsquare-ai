import random
import string


def generate_random_password(length=12, use_uppercase=True, use_digits=True, use_special_chars=True):
    """
    Generates a random password with the specified length and character types.

    :param length: Length of the password (default is 12).
    :param use_uppercase: Whether to include uppercase letters (default is True).
    :param use_digits: Whether to include digits (default is True).
    :param use_special_chars: Whether to include special characters (default is True).
    :return: A random password string.
    """
    if length < 1:
        raise ValueError("Password length must be at least 1.")

    lower_case = string.ascii_lowercase
    upper_case = string.ascii_uppercase if use_uppercase else ''
    digits = string.digits if use_digits else ''
    special_chars = string.punctuation if use_special_chars else ''

    all_characters = lower_case + upper_case + digits + special_chars

    if not all_characters:
        raise ValueError("At least one character type must be selected.")

    password = ''.join(random.choice(all_characters) for _ in range(length))

    return password
