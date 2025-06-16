# 1. Fixed-size sliding window: maximum sum of subarray of size k
def max_sum_subarray(arr, k):
    n = len(arr)
    if n < k:
        return -1
    window_sum = sum(arr[:k])
    max_sum = window_sum
    for i in range(k, n):
        window_sum += arr[i] - arr[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum


# 2. Variable-size sliding window: smallest subarray with sum >= target
def min_subarray_len(target, arr):
    n = len(arr)
    left = 0
    current_sum = 0
    min_length = float('inf')

    for right in range(n):
        current_sum += arr[right]

        # Shrink window from left as long as sum >= target
        while current_sum >= target:
            min_length = min(min_length, right - left + 1)
            current_sum -= arr[left]
            left += 1

    return min_length if min_length != float('inf') else 0


# 3. Sliding window with frequency map: longest substring with at most k distinct chars
def length_of_longest_substring_k_distinct(s, k):
    from collections import defaultdict
    count = defaultdict(int)
    left = 0
    max_length = 0
    distinct = 0

    for right in range(len(s)):
        if count[s[right]] == 0:
            distinct += 1
        count[s[right]] += 1

        while distinct > k:
            count[s[left]] -= 1
            if count[s[left]] == 0:
                distinct -= 1
            left += 1

        max_length = max(max_length, right - left + 1)
    return max_length


# 4. Sliding window: longest substring without repeating characters
def length_of_longest_substring(s):
    from collections import defaultdict
    count = defaultdict(int)
    left = 0
    max_length = 0

    for right in range(len(s)):
        count[s[right]] += 1

        # shrink window if duplicate found
        while count[s[right]] > 1:
            count[s[left]] -= 1
            left += 1

        max_length = max(max_length, right - left + 1)

    return max_length


if __name__ == "__main__":
    arr = [2, 3, 1, 2, 4, 3]
    print("Max sum subarray of size 3:", max_sum_subarray(arr, 3))  # 9

    target = 7
    print("Min subarray length with sum >= 7:", min_subarray_len(target, arr))  # 2 ([4,3])

    s1 = "eceba"
    k = 2
    print("Longest substring with at most 2 distinct chars:", length_of_longest_substring_k_distinct(s1, k))  # 3 ("ece")

    s2 = "abcabcbb"
    print("Longest substring without repeating chars:", length_of_longest_substring(s2))  # 3 ("abc")
