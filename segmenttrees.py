class SegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (2 * self.n)
        # Build the tree by inserting leaves
        for i in range(self.n):
            self.tree[self.n + i] = data[i]
        # Build internal nodes
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[i << 1] + self.tree[i << 1 | 1]

    def update(self, index, value):
        # Set value at position index
        pos = index + self.n
        self.tree[pos] = value
        # Move upward and update parents
        pos >>= 1
        while pos > 0:
            self.tree[pos] = self.tree[pos << 1] + self.tree[pos << 1 | 1]
            pos >>= 1

    def query(self, left, right):
        # Range sum query on interval [left, right)
        result = 0
        left += self.n
        right += self.n
        while left < right:
            if left & 1:
                result += self.tree[left]
                left += 1
            if right & 1:
                right -= 1
                result += self.tree[right]
            left >>= 1
            right >>= 1
        return result


# Example usage:
if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11]
    seg_tree = SegmentTree(arr)
    print(seg_tree.query(1, 4))  # sum of arr[1:4] = 3+5+7=15
    seg_tree.update(1, 10)       # arr[1] = 10 now
    print(seg_tree.query(1, 4))  # sum = 10+5+7=22
