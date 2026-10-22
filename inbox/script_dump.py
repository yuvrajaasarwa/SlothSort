"""
Bubble Sort Algorithm Demo
A simple sorting routine for an unsorted integer array.
Time Complexity: O(n^2), Space Complexity: O(1)
"""

def bubble_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

if __name__ == "__main__":
    test_nums = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original array: {test_nums}")
    sorted_nums = bubble_sort(test_nums)
    print(f"Sorted array:   {sorted_nums}")
