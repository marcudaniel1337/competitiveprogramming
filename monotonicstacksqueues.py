# -------------------
# Monotonic Stack Variants
# -------------------

def next_greater_elements(nums):
    """Next Greater Element to the right"""
    n = len(nums)
    res = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            res[idx] = nums[i]
        stack.append(i)
    return res

def next_smaller_elements(nums):
    """Next Smaller Element to the right"""
    n = len(nums)
    res = [-1] * n
    stack = []
    for i in range(n):
        while stack and nums[i] < nums[stack[-1]]:
            idx = stack.pop()
            res[idx] = nums[i]
        stack.append(i)
    return res

def previous_greater_elements(nums):
    """Previous Greater Element to the left"""
    n = len(nums)
    res = [-1] * n
    stack = []
    for i in range(n-1, -1, -1):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            res[idx] = nums[i]
        stack.append(i)
    return res

def previous_smaller_elements(nums):
    """Previous Smaller Element to the left"""
    n = len(nums)
    res = [-1] * n
    stack = []
    for i in range(n-1, -1, -1):
        while stack and nums[i] < nums[stack[-1]]:
            idx = stack.pop()
            res[idx] = nums[i]
        stack.append(i)
    return res


# -------------------
# Monotonic Queue Variants
# -------------------

from collections import deque

def max_sliding_window(nums, k):
    """Max in each sliding window of size k"""
    dq = deque()
    res = []
    for i, num in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] < num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res

def min_sliding_window(nums, k):
    """Min in each sliding window of size k"""
    dq = deque()
    res = []
    for i, num in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and nums[dq[-1]] > num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res

# -------------------
# Utility: Largest Rectangle in Histogram (classic monotonic stack)
# -------------------

def largest_rectangle_area(heights):
    """Largest rectangle in histogram"""
    stack = []
    max_area = 0
    heights.append(0)  # Sentinel to pop all at end
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    heights.pop()
    return max_area


# -------------------
# Utility: Trapping Rain Water (two-pointer + monotonic stack)
# -------------------

def trap_rain_water(height):
    """Compute how much water is trapped"""
    stack = []
    water = 0
    for i, h in enumerate(height):
        while stack and h > height[stack[-1]]:
            top = stack.pop()
            if not stack:
                break
            distance = i - stack[-1] - 1
            bounded_height = min(h, height[stack[-1]]) - height[top]
            water += distance * bounded_height
        stack.append(i)
    return water


if __name__ == "__main__":
    arr = [2, 1, 2, 4, 3]

    print("Next Greater:", next_greater_elements(arr))
    print("Next Smaller:", next_smaller_elements(arr))
    print("Previous Greater:", previous_greater_elements(arr))
    print("Previous Smaller:", previous_smaller_elements(arr))

    print("Max sliding window k=3:", max_sliding_window([1,3,-1,-3,5,3,6,7], 3))
    print("Min sliding window k=3:", min_sliding_window([1,3,-1,-3,5,3,6,7], 3))

    print("Largest rectangle area:", largest_rectangle_area([2,1,5,6,2,3]))
    print("Trapped rain water:", trap_rain_water([0,1,0,2,1,0,1,3,2,1,2,1]))
