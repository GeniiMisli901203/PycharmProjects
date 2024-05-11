import pytest
from binary_search import binary_search

@pytest.mark.parametrize("arr, x, expected", [
    ([1, 2, 3, 4, 5], 3, 2),
    ([1, 2, 3, 4, 5], 1, 0),
    ([1, 2, 3, 4, 5], 5, 4),
    ([1, 2, 3, 4, 5], 0, -1),
    ([1, 2, 3, 3, 3, 4, 5], 3, 2),
])
def test_binary_search(arr, x, expected):
    assert binary_search(arr, x) == expected
