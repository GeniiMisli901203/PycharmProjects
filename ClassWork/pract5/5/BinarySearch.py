import hypothesis.strategies as st
import unittest
from hypothesis import given

def binary_search(arr, x):
    left = 0
    right = len(arr)
    while left <= right:
        mid = round((left + right) / 2)
        if arr[mid] == x:
            return mid
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid
    return -1

class TestBinarySearch(unittest.TestCase):
    @given(st.lists(st.integers(), min_size=1), st.integers())
    def test_binary_search(self, arr, x):
        # Тест для отсортированного массива
        arr.sort()
        result = binary_search(arr, x)

        if result == -1:
            self.assertNotIn(x, arr)
        else:
            self.assertEqual(arr[result], x)

if __name__ == '__main__':
    unittest.main()
