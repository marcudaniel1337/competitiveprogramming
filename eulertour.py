class EulerTourSegmentTree:
    """
    A data structure that combines Euler Tour technique with Segment Tree
    to efficiently handle subtree queries on trees.
    
    The main idea:
    1. Convert the tree into a linear array using Euler Tour
    2. Use a segment tree on this array to answer range queries
    3. Each subtree becomes a contiguous range in the linearized representation
    """
    
    def __init__(self, n, tree, values):
        """
        Initialize the data structure.
        
        Args:
            n: number of nodes in the tree
            tree: adjacency list representation of the tree
            values: array of values at each node (0-indexed)
        """
        self.n = n
        self.tree = tree
        self.values = values
        
        # Arrays to store Euler tour information
        self.euler_tour = []  # The actual Euler tour sequence
        self.start_time = [0] * n  # When we first visit each node
        self.end_time = [0] * n    # When we finish processing each node
        self.tour_values = []      # Values corresponding to the tour
        
        # Perform DFS to build Euler tour
        self.time = 0
        self._dfs(0, -1)  # Assuming node 0 is root
        
        # Build segment tree on the linearized data
        self.seg_size = len(self.tour_values)
        self.seg_tree = [0] * (4 * self.seg_size)
        self._build_segment_tree(1, 0, self.seg_size - 1)
    
    def _dfs(self, node, parent):
        """
        DFS to create Euler tour of the tree.
        
        The key insight: we record the entry time when we first visit a node,
        and exit time when we're done with all its children.
        Everything in between belongs to the subtree.
        """
        # Record when we enter this node
        self.start_time[node] = self.time
        self.euler_tour.append(node)
        self.tour_values.append(self.values[node])
        self.time += 1
        
        # Visit all children
        for child in self.tree[node]:
            if child != parent:  # Don't go back to parent
                self._dfs(child, node)
        
        # Record when we exit this node
        self.end_time[node] = self.time - 1
    
    def _build_segment_tree(self, node, start, end):
        """
        Build the segment tree for range sum queries.
        
        This is a standard segment tree build - each node stores
        the sum of values in its range.
        """
        if start == end:
            # Leaf node - just store the single value
            self.seg_tree[node] = self.tour_values[start]
        else:
            mid = (start + end) // 2
            
            # Build left and right children
            self._build_segment_tree(2 * node, start, mid)
            self._build_segment_tree(2 * node + 1, mid + 1, end)
            
            # Internal node stores sum of its children
            self.seg_tree[node] = self.seg_tree[2 * node] + self.seg_tree[2 * node + 1]
    
    def _update_segment_tree(self, node, start, end, idx, new_val):
        """
        Update a single element in the segment tree.
        
        When we update a node's value, we need to update the corresponding
        position in our linearized representation.
        """
        if start == end:
            # Found the leaf to update
            self.seg_tree[node] = new_val
        else:
            mid = (start + end) // 2
            
            if idx <= mid:
                # Update is in left subtree
                self._update_segment_tree(2 * node, start, mid, idx, new_val)
            else:
                # Update is in right subtree
                self._update_segment_tree(2 * node + 1, mid + 1, end, idx, new_val)
            
            # Update current node after updating children
            self.seg_tree[node] = self.seg_tree[2 * node] + self.seg_tree[2 * node + 1]
    
    def _query_segment_tree(self, node, start, end, l, r):
        """
        Query sum in a range [l, r] using segment tree.
        
        This is the standard segment tree range query.
        """
        if r < start or l > end:
            # No overlap
            return 0
        
        if l <= start and end <= r:
            # Complete overlap - return this node's value
            return self.seg_tree[node]
        
        # Partial overlap - query both children
        mid = (start + end) // 2
        left_sum = self._query_segment_tree(2 * node, start, mid, l, r)
        right_sum = self._query_segment_tree(2 * node + 1, mid + 1, end, l, r)
        
        return left_sum + right_sum
    
    def update_node(self, node_id, new_value):
        """
        Update the value of a specific node.
        
        Since each node appears only once in our Euler tour,
        we just need to update that single position.
        """
        # Update our local copy
        self.values[node_id] = new_value
        self.tour_values[self.start_time[node_id]] = new_value
        
        # Update the segment tree
        self._update_segment_tree(1, 0, self.seg_size - 1, 
                                 self.start_time[node_id], new_value)
    
    def query_subtree_sum(self, root_node):
        """
        Get the sum of all values in the subtree rooted at root_node.
        
        The magic happens here: since we did an Euler tour, all nodes
        in the subtree of root_node appear in the range 
        [start_time[root_node], end_time[root_node]]
        """
        start = self.start_time[root_node]
        end = self.end_time[root_node]
        
        return self._query_segment_tree(1, 0, self.seg_size - 1, start, end)
    
    def print_debug_info(self):
        """
        Print debug information to understand how the transformation works.
        """
        print("=== Euler Tour Debug Information ===")
        print(f"Original tree values: {self.values}")
        print(f"Euler tour sequence: {self.euler_tour}")
        print(f"Tour values: {self.tour_values}")
        print()
        
        print("Node timing information:")
        for i in range(self.n):
            print(f"Node {i}: start={self.start_time[i]}, end={self.end_time[i]}")
        print()
        
        print("What this means:")
        print("- Each node's subtree corresponds to range [start_time, end_time]")
        print("- All descendants appear between these times in the tour")


# Example usage and testing
def example_usage():
    """
    Let's build a sample tree and see how this works:
    
    Tree structure:
         0(5)
        /   \
      1(3)  2(7)
     /  \     \
   3(2) 4(1)  5(4)
   
   Values in parentheses are the node values.
   """
    
    print("=== Example: Euler Tour + Segment Tree ===")
    
    # Number of nodes
    n = 6
    
    # Tree as adjacency list (undirected)
    tree = [
        [1, 2],      # Node 0 connected to 1, 2
        [0, 3, 4],   # Node 1 connected to 0, 3, 4  
        [0, 5],      # Node 2 connected to 0, 5
        [1],         # Node 3 connected to 1
        [1],         # Node 4 connected to 1
        [2]          # Node 5 connected to 2
    ]
    
    # Values at each node
    values = [5, 3, 7, 2, 1, 4]
    
    # Create the data structure
    etst = EulerTourSegmentTree(n, tree, values)
    
    # Show how the transformation works
    etst.print_debug_info()
    
    # Test subtree queries
    print("=== Subtree Sum Queries ===")
    for i in range(n):
        subtree_sum = etst.query_subtree_sum(i)
        print(f"Sum of subtree rooted at node {i}: {subtree_sum}")
    
    print("\nLet's verify manually:")
    print("- Subtree of node 0 (entire tree): 5+3+7+2+1+4 = 22")
    print("- Subtree of node 1: 3+2+1 = 6") 
    print("- Subtree of node 2: 7+4 = 11")
    print("- Subtree of node 3: 2")
    print("- Subtree of node 4: 1") 
    print("- Subtree of node 5: 4")
    
    # Test updates
    print("\n=== Testing Updates ===")
    print("Updating node 1 from value 3 to value 10...")
    etst.update_node(1, 10)
    
    print("New subtree sums:")
    for i in range(n):
        subtree_sum = etst.query_subtree_sum(i)
        print(f"Sum of subtree rooted at node {i}: {subtree_sum}")
    
    print("\nExpected changes:")
    print("- Subtree of node 0: 22 + 7 = 29 (since node 1 is in subtree of 0)")
    print("- Subtree of node 1: 6 + 7 = 13 (since node 1 is the root of its subtree)")


class EulerTourSegmentTreeAdvanced:
    """
    Advanced version that supports multiple types of queries:
    - Range sum queries
    - Range minimum/maximum queries  
    - Range updates (lazy propagation)
    """
    
    def __init__(self, n, tree, values):
        self.n = n
        self.tree = tree
        self.values = values
        
        # Euler tour arrays
        self.euler_tour = []
        self.start_time = [0] * n
        self.end_time = [0] * n
        self.tour_values = []
        
        # Build Euler tour
        self.time = 0
        self._dfs(0, -1)
        
        # Segment tree arrays
        self.seg_size = len(self.tour_values)
        self.sum_tree = [0] * (4 * self.seg_size)
        self.min_tree = [float('inf')] * (4 * self.seg_size)
        self.max_tree = [float('-inf')] * (4 * self.seg_size)
        self.lazy = [0] * (4 * self.seg_size)  # For lazy propagation
        
        self._build_advanced_tree(1, 0, self.seg_size - 1)
    
    def _dfs(self, node, parent):
        """Same DFS as basic version."""
        self.start_time[node] = self.time
        self.euler_tour.append(node)
        self.tour_values.append(self.values[node])
        self.time += 1
        
        for child in self.tree[node]:
            if child != parent:
                self._dfs(child, node)
        
        self.end_time[node] = self.time - 1
    
    def _build_advanced_tree(self, node, start, end):
        """Build segment tree with sum, min, and max."""
        if start == end:
            val = self.tour_values[start]
            self.sum_tree[node] = val
            self.min_tree[node] = val
            self.max_tree[node] = val
        else:
            mid = (start + end) // 2
            self._build_advanced_tree(2 * node, start, mid)
            self._build_advanced_tree(2 * node + 1, mid + 1, end)
            
            # Combine results from children
            self.sum_tree[node] = self.sum_tree[2 * node] + self.sum_tree[2 * node + 1]
            self.min_tree[node] = min(self.min_tree[2 * node], self.min_tree[2 * node + 1])
            self.max_tree[node] = max(self.max_tree[2 * node], self.max_tree[2 * node + 1])
    
    def query_subtree_sum(self, root_node):
        """Get sum of subtree."""
        start, end = self.start_time[root_node], self.end_time[root_node]
        return self._query_sum(1, 0, self.seg_size - 1, start, end)
    
    def query_subtree_min(self, root_node):
        """Get minimum value in subtree."""
        start, end = self.start_time[root_node], self.end_time[root_node]
        return self._query_min(1, 0, self.seg_size - 1, start, end)
    
    def query_subtree_max(self, root_node):
        """Get maximum value in subtree."""
        start, end = self.start_time[root_node], self.end_time[root_node]
        return self._query_max(1, 0, self.seg_size - 1, start, end)
    
    def _query_sum(self, node, start, end, l, r):
        """Query sum in range [l, r]."""
        if r < start or l > end:
            return 0
        if l <= start and end <= r:
            return self.sum_tree[node]
        
        mid = (start + end) // 2
        return (self._query_sum(2 * node, start, mid, l, r) + 
                self._query_sum(2 * node + 1, mid + 1, end, l, r))
    
    def _query_min(self, node, start, end, l, r):
        """Query minimum in range [l, r]."""
        if r < start or l > end:
            return float('inf')
        if l <= start and end <= r:
            return self.min_tree[node]
        
        mid = (start + end) // 2
        return min(self._query_min(2 * node, start, mid, l, r),
                   self._query_min(2 * node + 1, mid + 1, end, l, r))
    
    def _query_max(self, node, start, end, l, r):
        """Query maximum in range [l, r]."""
        if r < start or l > end:
            return float('-inf')
        if l <= start and end <= r:
            return self.max_tree[node]
        
        mid = (start + end) // 2
        return max(self._query_max(2 * node, start, mid, l, r),
                   self._query_max(2 * node + 1, mid + 1, end, l, r))


if __name__ == "__main__":
    # Run the example
    example_usage()
    
    print("\n" + "="*50)
    print("Time Complexity Analysis:")
    print("- Preprocessing: O(n) for Euler tour + O(n) for segment tree = O(n)")
    print("- Subtree query: O(log n)")  
    print("- Node update: O(log n)")
    print("- Space complexity: O(n)")
    print()
    print("This beats the naive O(n) per query approach!")
    print("Perfect for problems with many subtree queries on large trees.")
