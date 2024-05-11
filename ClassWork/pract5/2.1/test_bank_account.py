import pytest
from bucketsort import bucketsort

@pytest.mark.parametrize("arr, k, expected_sorted_arr", [
    ([3, 5, 2, 1, 4, 6, 2], 7, [1, 2, 2, 3, 4, 5, 6]),
    ([0, 0, 1, 2, 3, 4, 5], 6, [0, 0, 1, 2, 3, 4, 5]),
    ([5, 4, 3, 2, 1, 0], 6, [0, 1, 2, 3, 4, 5]),
    ([1, 1, 2, 2, 3, 3], 4, [1, 1, 2, 2, 3, 3]),
    ([], 5, []),
    ([3], 4, [3]),
])
def test_bucketsort(arr, k, expected_sorted_arr):
    assert bucketsort(arr, k) == expected_sorted_arr

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_unconfigure(config):
    yield
    if config.hook.pytest_sessionfinish.called and not config.hook.pytest_sessionfinish.failed:
        print("\nТестирование пройдено")