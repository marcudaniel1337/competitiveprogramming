from collections import defaultdict, deque

class CentroidDecomposition:
    """
    Centroid Decomposition implementation for efficient path counting in trees.
    
    The main idea: We recursively find the centroid (a node whose removal splits 
    the tree into components of size ≤ n/2), process all paths through it, 
    then recursively solve for each component.
    
    This gives us O(n log n) complexity for many tree problems!
    """
    
    def __init__(self, n):
        # n is the number of nodes (assuming 0-indexed)
        self.n = n
        # Adjacency list representation of our tree
        self.graph = defaultdict(list)
        # Keep track of which nodes we've already processed as centroids
        self.removed = [False] * n
        # Store subtree sizes for centroid finding
        self.subtree_size = [0] * n
    
    def add_edge(self, u, v):
        """Add an undirected edge between nodes u and v"""
        self.graph[u].append(v)
        self.graph[v].append(u)
    
    def get_subtree_size(self, node, parent):
        """
        Calculate the size of subtree rooted at 'node'.
        We need this to find the centroid efficiently.
        """
        self.subtree_size[node] = 1  # Count the node itself
        
        # Visit all children and add their subtree sizes
        for neighbor in self.graph[node]:
            if neighbor != parent and not self.removed[neighbor]:
                self.subtree_size[node] += self.get_subtree_size(neighbor, node)
        
        return self.subtree_size[node]
    
    def find_centroid(self, node, parent, tree_size):
        """
        Find the centroid of the current tree component.
        
        A centroid is a node such that when removed, no remaining 
        component has size > tree_size/2.
        
        Why is this useful? It guarantees balanced decomposition!
        """
        # Check if current node can be a centroid
        is_centroid = True
        
        for neighbor in self.graph[node]:
            if neighbor != parent and not self.removed[neighbor]:
                # If any subtree is too large, this can't be centroid
                if self.subtree_size[neighbor] > tree_size // 2:
                    is_centroid = False
                    # Recursively search in the large subtree
                    return self.find_centroid(neighbor, node, tree_size)
        
        # Also check the "upward" component (parent side)
        if parent != -1:
            upward_size = tree_size - self.subtree_size[node]
            if upward_size > tree_size // 2:
                is_centroid = False
        
        # If we reach here and is_centroid is True, we found our centroid!
        return node if is_centroid else -1
    
    def get_distances(self, start, max_dist=None):
        """
        BFS to get distances from start node to all reachable nodes.
        This is used to find all paths of specific lengths through the centroid.
        
        Returns: dictionary mapping node -> distance from start
        """
        distances = {}
        queue = deque([(start, 0)])  # (node, distance)
        distances[start] = 0
        
        while queue:
            node, dist = queue.popleft()
            
            # If we have a max distance limit and exceeded it, skip
            if max_dist is not None and dist >= max_dist:
                continue
            
            # Explore all unremoved neighbors
            for neighbor in self.graph[node]:
                if not self.removed[neighbor] and neighbor not in distances:
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))
        
        return distances
    
    def count_paths_with_length(self, target_length):
        """
        Count all simple paths in the tree that have exactly 'target_length' edges.
        
        This is the main function that uses centroid decomposition!
        """
        self.target_length = target_length
        self.total_paths = 0
        
        # Start the recursive decomposition from any node (let's use 0)
        self._decompose(0)
        
        return self.total_paths
    
    def _decompose(self, start_node):
        """
        The heart of centroid decomposition!
        
        1. Find the centroid of current component
        2. Count all paths through this centroid
        3. Remove centroid and recursively solve subproblems
        """
        # First, calculate subtree sizes for centroid finding
        tree_size = self.get_subtree_size(start_node, -1)
        
        # Find the centroid of this component
        centroid = self.find_centroid(start_node, -1, tree_size)
        
        # Count paths passing through this centroid
        self._count_paths_through_centroid(centroid)
        
        # Mark centroid as removed (so it won't be considered in subproblems)
        self.removed[centroid] = True
        
        # Recursively decompose each remaining component
        for neighbor in self.graph[centroid]:
            if not self.removed[neighbor]:
                # Each neighbor represents a separate component now
                self._decompose(neighbor)
    
    def _count_paths_through_centroid(self, centroid):
        """
        Count all paths of target length that pass through the centroid.
        
        Key insight: Any path through centroid goes from some node in 
        subtree A to some node in subtree B (where A ≠ B).
        
        We use the principle: 
        - Count paths from centroid to all nodes in each subtree
        - For target length k, combine paths of length i from subtree A 
          with paths of length (k-i) from subtree B
        """
        # Get all distances from centroid (this includes all subtrees)
        all_distances = self.get_distances(centroid, self.target_length)
        
        # Group nodes by which subtree they belong to
        subtree_distances = []
        
        for neighbor in self.graph[centroid]:
            if not self.removed[neighbor]:
                # Get distances within this specific subtree
                subtree_dist = self.get_distances(neighbor, self.target_length - 1)
                # Add 1 to each distance (since we're measuring from centroid)
                subtree_dist = {node: dist + 1 for node, dist in subtree_dist.items()}
                subtree_distances.append(subtree_dist)
        
        # Now count valid path combinations between different subtrees
        for i in range(len(subtree_distances)):
            for j in range(i + 1, len(subtree_distances)):
                # Count paths from subtree i to subtree j
                self._count_between_subtrees(
                    subtree_distances[i], 
                    subtree_distances[j]
                )
        
        # Don't forget paths that start/end at the centroid itself!
        if self.target_length in all_distances.values():
            # Count how many nodes are exactly target_length away
            nodes_at_target_dist = sum(1 for dist in all_distances.values() 
                                     if dist == self.target_length)
            self.total_paths += nodes_at_target_dist
    
    def _count_between_subtrees(self, subtree1_distances, subtree2_distances):
        """
        Count valid paths between two different subtrees.
        
        For each node in subtree1 at distance d1, we need nodes in subtree2 
        at distance (target_length - d1) to form a valid path.
        """
        # Create frequency map for subtree2 distances
        dist_freq = defaultdict(int)
        for dist in subtree2_distances.values():
            dist_freq[dist] += 1
        
        # For each node in subtree1, find matching nodes in subtree2
        for dist1 in subtree1_distances.values():
            needed_dist = self.target_length - dist1
            if needed_dist in dist_freq:
                # Each node at dist1 can pair with each node at needed_dist
                self.total_paths += dist_freq[needed_dist]

# Example usage and testing
def example_usage():
    """
    Let's create a simple tree and count paths of length 2.
    
    Tree structure:
        0
       / \
      1   2
     /   / \
    3   4   5
    
    Paths of length 2: (3,1,0), (0,1,3), (0,2,4), (4,2,0), 
                       (0,2,5), (5,2,0), (4,2,5), (5,2,4)
    Total: 8 paths
    """
    
    print("Creating example tree...")
    cd = CentroidDecomposition(6)  # 6 nodes: 0,1,2,3,4,5
    
    # Add edges to form the tree above
    edges = [(0,1), (0,2), (1,3), (2,4), (2,5)]
    for u, v in edges:
        cd.add_edge(u, v)
    
    print("Tree edges:", edges)
    
    # Count paths of length 2
    target_length = 2
    result = cd.count_paths_with_length(target_length)
    
    print(f"Number of paths with length {target_length}: {result}")
    
    # Let's also try length 1 (should be 10: each edge counted twice)
    cd2 = CentroidDecomposition(6)
    for u, v in edges:
        cd2.add_edge(u, v)
    
    result2 = cd2.count_paths_with_length(1)
    print(f"Number of paths with length 1: {result2}")

def stress_test():
    """
    Test with a larger tree to see the efficiency.
    Let's create a path graph: 0-1-2-3-...-n
    """
    print("\nStress testing with path graph...")
    n = 1000
    cd = CentroidDecomposition(n)
    
    # Create path: 0-1-2-3-...-999
    for i in range(n-1):
        cd.add_edge(i, i+1)
    
    import time
    start_time = time.time()
    
    # Count paths of length 10
    result = cd.count_paths_with_length(10)
    
    end_time = time.time()
    
    print(f"Path graph with {n} nodes:")
    print(f"Paths of length 10: {result}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # For a path graph, paths of length k should be 2*(n-k)
    # (each internal segment of length k can be traversed in 2 directions)
    expected = 2 * (n - 10) if n > 10 else 0
    print(f"Expected: {expected}")
    print(f"Correct: {result == expected}")

if __name__ == "__main__":
    example_usage()
    stress_test()
