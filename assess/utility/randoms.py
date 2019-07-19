import string
import random


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Generation of unique IDs based on given chars and a specified size.

    :param size: Length of string
    :param chars: Chars contained in string
    :return: Unique ID
    """
    return ''.join(random.choice(chars) for _ in range(size))
