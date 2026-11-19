from pin_extension import (
    BruteForceCracker, PinCracker, PinLock, all_codes, crack, feedback,
)


def test_feedback_counts_digits_in_the_right_place():
    assert feedback("123", "123") == 3
    assert feedback("123", "124") == 2
    assert feedback("123", "321") == 1     # only the middle 2 is in place
    assert feedback("123", "456") == 0


def test_all_codes_has_one_thousand_codes():
    codes = all_codes(3)
    assert len(codes) == 1000
    assert len(set(codes)) == 1000
    assert codes[0] == "000" and codes[-1] == "999"


def test_lock_only_opens_with_the_right_code():
    lock = PinLock("417")
    assert lock.try_code("418") == 2
    assert not lock.unlocked
    assert lock.try_code("417") == 3
    assert lock.unlocked
    assert lock.attempts == 2


def test_cracker_opens_the_lock():
    lock = PinLock("902")
    guesses = crack(lock, PinCracker(seed=1))
    assert lock.unlocked
    assert guesses == lock.attempts


def test_cracker_always_succeeds_quickly():
    for secret in all_codes(3)[::7]:                  # every 7th code, 143 PINs
        lock = PinLock(secret)
        guesses = crack(lock, PinCracker(seed=2))
        assert lock.unlocked
        assert guesses <= 25


def test_same_seed_same_number_of_guesses():
    first = crack(PinLock("358"), PinCracker(seed=5))
    second = crack(PinLock("358"), PinCracker(seed=5))
    assert first == second


def test_brute_force_needs_the_secret_number_plus_one_guesses():
    lock = PinLock("250")
    assert crack(lock, BruteForceCracker()) == 251


def test_feedback_beats_brute_force():
    smart = []
    for secret in all_codes(3)[::13]:
        smart.append(crack(PinLock(secret), PinCracker(seed=3)))
    assert sum(smart) / len(smart) < 20               # brute force averages about 500


if __name__ == "__main__":
    test_feedback_counts_digits_in_the_right_place()
    test_all_codes_has_one_thousand_codes()
    test_lock_only_opens_with_the_right_code()
    test_cracker_opens_the_lock()
    test_cracker_always_succeeds_quickly()
    test_same_seed_same_number_of_guesses()
    test_brute_force_needs_the_secret_number_plus_one_guesses()
    test_feedback_beats_brute_force()
    print("All PIN tests passed")
