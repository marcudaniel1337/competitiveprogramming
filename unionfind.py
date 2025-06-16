class UnionFind:
    def __init__(self, n):
        # parent[i] points to parent of i, or to itself if i is root
        self.parent = list(range(n))
        # size[i] tracks size of tree rooted at i (for union by size)
        self.size = [1] * n

    def find(self, x):
        # Path compression: flattens tree for faster future queries
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        # Union by size: attach smaller tree under bigger tree
        rootA = self.find(a)
        rootB = self.find(b)
        if rootA != rootB:
            if self.size[rootA] < self.size[rootB]:
                rootA, rootB = rootB, rootA
            self.parent[rootB] = rootA
            self.size[rootA] += self.size[rootB]

    def connected(self, a, b):
        # Check if two nodes share the same root (are in same set)
        return self.find(a) == self.find(b)


if __name__ == "__main__":
    uf = UnionFind(10)
    uf.union(1, 2)
    uf.union(2, 5)
    uf.union(5, 6)
    uf.union(3, 4)

    print(uf.connected(1, 5))  # True
    print(uf.connected(1, 3))  # False
    uf.union(1, 3)
    print(uf.connected(1, 3))  # True
