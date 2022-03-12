from django.contrib.auth.hashers import PBKDF2PasswordHasher

from .settings import *


class MyPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    """
    A subclass of PBKDF2PasswordHasher that uses 1 iteration.
    This is for test purposes only. Never use anywhere else.
    """

    iterations = 1


PASSWORD_HASHERS = [
    "sportsnet.settings_test.MyPBKDF2PasswordHasher",
]
