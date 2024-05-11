import hypothesis.strategies as st
import hypothesis

def rle_encode(sequence):
    encoded = []
    i = 0
    while i < len(sequence):
        count = 1
        while i + 1 < len(sequence) and sequence[i] == sequence[i + 1]:
            count += 1
            i += 1
        encoded.append((sequence[i], count))
        i += 1
    return encoded

def rle_decode(encoded_sequence):
    decoded = []
    for item, count in encoded_sequence:
        decoded.extend([item] * count)
    return decoded

@hypothesis.settings(deadline=None)
@hypothesis.given(st.lists(st.integers(), min_size=1, max_size=5))
def test_rle_encode_decode(sequence):
    encoded = rle_encode(sequence)
    decoded = rle_decode(encoded)
    assert decoded == sequence

@hypothesis.settings(deadline=None)
@hypothesis.given(st.lists(st.tuples(st.integers(), st.integers(min_value=1)), min_size=1, max_size=5))
def test_rle_decode_encode(encoded_sequence):
    decoded = rle_decode(encoded_sequence)
    re_encoded = rle_encode(decoded)
    assert re_encoded == encoded_sequence

if __name__ == '__main__':
    hypothesis.main()
