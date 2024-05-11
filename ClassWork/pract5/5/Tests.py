import hypothesis.strategies as st
import unittest
from hypothesis import given
from .BinarySearch import binary_search
class Tests(unittest.TestCase):
    @given(st.lists(st.integers(), min_size=1), st.integers())
    def test_binary_search(self, arr, x):
        # Тест для отсортированного массива
        arr.sort()
        result = binary_search(arr, x)

        if result == -1:
            self.assertNotIn(x, arr)
        else:
            self.assertEqual(arr[result], x)