# Standard Binary Search (find index of target in sorted array, or -1 if not found)
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# Find the leftmost (first) occurrence of target in sorted array
def binary_search_left(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    if left < len(arr) and arr[left] == target:
        return left
    return -1


# Find the rightmost (last) occurrence of target in sorted array
def binary_search_right(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid
    if left > 0 and arr[left - 1] == target:
        return left - 1
    return -1


# Find the first element greater than or equal to target
def lower_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left  # index where target can be inserted


# Find the first element strictly greater than target
def upper_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid
    return left


# Binary search on answer space (example: sqrt of x)
def binary_search_sqrt(x, precision=1e-6):
    if x < 2:
        return x
    left, right = 0, x
    while right - left > precision:
        mid = (left + right) / 2
        if mid * mid > x:
            right = mid
        else:
            left = mid
    return left


if __name__ == "__main__":
    arr = [1, 2, 2, 2, 3, 4, 5]

    print("Standard Binary Search for 2:", binary_search(arr, 2))
    print("Leftmost occurrence of 2:", binary_search_left(arr, 2))
    print("Rightmost occurrence of 2:", binary_search_right(arr, 2))
    print("Lower bound for 2:", lower_bound(arr, 2))
    print("Upper bound for 2:", upper_bound(arr, 2))
    print("Square root of 10 approx:", binary_search_sqrt(10))
