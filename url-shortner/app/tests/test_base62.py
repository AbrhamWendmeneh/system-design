import pytest

from app import ALPHABET, base62_decode, base62_encode


@pytest.mark.parametrize(
    "number",
    [0, 1, 9, 10, 35, 36, 61, 62, 63, 3_843, 3_844, 1_000_000],
)
def test_base62_round_trip(number):
    encoded = base62_encode(number)

    assert base62_decode(encoded) == number
    assert set(encoded) <= set(ALPHABET)


def test_base62_alphabet_has_62_unique_characters():
    assert len(ALPHABET) == 62
    assert len(set(ALPHABET)) == 62


@pytest.mark.parametrize("value", ["", "abc-123", "favicon.ico", " "])
def test_base62_decode_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="Invalid base62 string"):
        base62_decode(value)
