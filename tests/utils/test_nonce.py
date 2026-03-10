from core.utils.nonce_manager import bump_nonce, get_nonce


def test_nonce_monotonic_per_key():
    key = "test_key_1"
    vals = [int(get_nonce(key)) for _ in range(10)]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))


def test_nonce_bump_increases_enough():
    key = "test_key_2"
    before = int(get_nonce(key))
    bumped = int(bump_nonce(key))
    assert bumped - before >= 1_000_000
    after = int(get_nonce(key))
    assert int(after) >= bumped
