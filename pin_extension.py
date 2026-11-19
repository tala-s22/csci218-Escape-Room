"""Extension: a PIN lock that hides the key until it is cracked."""

import itertools
import random

PIN_DIGITS = 3


def feedback(secret, guess):
    """How many digits of the guess are in the right place."""
    return sum(1 for a, b in zip(secret, guess) if a == b)


def all_codes(digits=PIN_DIGITS):
    """Every possible PIN, as text: '000', '001', ..., '999'."""
    return ["".join(digits_tuple) for digits_tuple in itertools.product("0123456789", repeat=digits)]


class PinLock:
    """The lock on cell P. It only says how many digits are in the right place."""

    def __init__(self, secret):
        self.secret = secret
        self.attempts = 0
        self.unlocked = False

    def try_code(self, guess):
        self.attempts += 1
        result = feedback(self.secret, guess)
        if result == len(self.secret):
            self.unlocked = True
        return result


class PinCracker:
    """Cracks a PIN using the lock's feedback: it keeps only the codes that are still possible."""

    def __init__(self, digits=PIN_DIGITS, seed=0):
        self.rng = random.Random(seed)
        self.candidates = all_codes(digits)
        self.last_guess = None
        self.guesses = 0

    def next_guess(self):
        self.last_guess = self.rng.choice(self.candidates)
        self.guesses += 1
        return self.last_guess

    def learn(self, result):
        """Cross out every code that would not have given this result for the last guess."""
        self.candidates = [
            code for code in self.candidates
            if feedback(code, self.last_guess) == result
        ]


class BruteForceCracker:
    """Tries 000, 001, 002, ... in order and ignores the feedback."""

    def __init__(self, digits=PIN_DIGITS):
        self.digits = digits
        self.guesses = 0

    def next_guess(self):
        guess = str(self.guesses).zfill(self.digits)
        self.guesses += 1
        return guess

    def learn(self, result):
        pass


def crack(lock, cracker, max_guesses=10000):
    """Keep guessing until the lock opens. Returns the number of guesses used."""
    while not lock.unlocked and cracker.guesses < max_guesses:
        guess = cracker.next_guess()
        result = lock.try_code(guess)
        cracker.learn(result)
    return cracker.guesses
