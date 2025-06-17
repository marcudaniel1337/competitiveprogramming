class HeavyLightDecomposition:
    """
    Heavy-Light Decomposition for efficient path queries on trees.
    
    The main idea is to decompose the tree into chains where each chain
    contains at most O(log n) "light" edges. This allows us to answer
    path queries in O(log^2 n) time.
    
    Key concepts:
    - Heavy edge: connects a node to its child with the largest subtree
    - Light edge: all other edges
    - Chain: maximal path of heavy edges
    """
    
    def __init__(self, n):
        """
        Initialize HLD for a tree with n nodes (0-indexed).
        
        Args:
            n: number of nodes in the tree
        """
        self.n = n
        self.graph = [[] for _ in range(n)]  # adjacency list
        
        # Arrays to store decomposition info
        self.parent = [-1] * n          # parent of each node
        self.depth = [0] * n            # depth from root
        self.subtree_size = [0] * n     # size of subtree rooted at each node
        self.heavy_child = [-1] * n     # heavy child of each node (-1 if none)
        
        # Chain decomposition info
        self.chain_head = [0] * n       # head of the chain containing each node
        self.chain_pos = [0] * n        # position of node within its chain
        self.chain_count = 0            # total number of chains
        
        # For range queries on chains - we'll use a simple array here
        # In practice, you'd want a segment tree or fenwick tree
        self.values = [0] * n           # node values
        
    def add_edge(self, u, v):
        """Add an undirected edge between nodes u and v."""
        self.graph[u].append(v)
        self.graph[v].append(u)
    
    def build(self, root=0):
        """
        Build the heavy-light decomposition starting from the given root.
        
        This is a two-step process:
        1. First DFS: compute parent, depth, subtree size, and heavy children
        2. Second DFS: decompose into chains
        """
        # Step 1: Find heavy children
        self._dfs_sizes(root, -1)
        
        # Step 2: Decompose into chains
        self._dfs_decompose(root, -1, root)
    
    def _dfs_sizes(self, node, par):
        """
        First DFS: compute subtree sizes and identify heavy children.
        
        A heavy child is the child with the largest subtree.
        This ensures that going down a heavy edge doesn't decrease
        the subtree size by more than half.
        """
        self.parent[node] = par
        self.subtree_size[node] = 1
        
        max_child_size = 0
        
        for child in self.graph[node]:
            if child == par:
                continue
                
            # Set depth of child
            self.depth[child] = self.depth[node] + 1
            
            # Recursively process child's subtree
            self._dfs_sizes(child, node)
            
            # Update our subtree size
            self.subtree_size[node] += self.subtree_size[child]
            
            # Check if this child should be our heavy child
            if self.subtree_size[child] > max_child_size:
                max_child_size = self.subtree_size[child]
                self.heavy_child[node] = child
    
    def _dfs_decompose(self, node, par, head):
        """
        Second DFS: decompose the tree into heavy chains.
        
        Each chain is a maximal path of heavy edges.
        We assign each node a position within its chain.
        """
        # This node belongs to the chain starting at 'head'
        self.chain_head[node] = head
        
        # If this is the start of a new chain, assign it a new chain ID
        if head == node:
            self.chain_pos[node] = self.chain_count
            self.chain_count += 1
        else:
            # Continue the current chain
            self.chain_pos[node] = self.chain_pos[self.parent[node]] + 1
        
        # First, process the heavy child (if it exists) to continue the chain
        if self.heavy_child[node] != -1:
            self._dfs_decompose(self.heavy_child[node], node, head)
        
        # Then process all light children, each starting a new chain
        for child in self.graph[node]:
            if child == par or child == self.heavy_child[node]:
                continue
            # Light edge - start a new chain
            self._dfs_decompose(child, node, child)
    
    def lca(self, u, v):
        """
        Find Lowest Common Ancestor of nodes u and v.
        
        We move up the lighter node until both nodes are in the same chain,
        then return the higher node in that chain.
        """
        # Keep moving up until both nodes are in the same chain
        while self.chain_head[u] != self.chain_head[v]:
            # Move the node that's in a chain with a deeper head
            if self.depth[self.chain_head[u]] > self.depth[self.chain_head[v]]:
                u = self.parent[self.chain_head[u]]
            else:
                v = self.parent[self.chain_head[v]]
        
        # Now both are in the same chain, return the higher one
        return u if self.depth[u] < self.depth[v] else v
    
    def path_query(self, u, v, query_type="sum"):
        """
        Answer a query on the path from u to v.
        
        The path is decomposed into O(log n) chain segments.
        We query each segment and combine the results.
        
        Args:
            u, v: endpoints of the path
            query_type: type of query ("sum", "max", "min")
        """
        lca_node = self.lca(u, v)
        
        # Query path from u to LCA
        result_u_to_lca = self._query_up(u, lca_node, query_type)
        
        # Query path from v to LCA  
        result_v_to_lca = self._query_up(v, lca_node, query_type)
        
        # Combine results (subtract LCA value since it's counted twice)
        lca_value = self.values[lca_node]
        
        if query_type == "sum":
            return result_u_to_lca + result_v_to_lca - lca_value
        elif query_type == "max":
            return max(result_u_to_lca, result_v_to_lca)
        elif query_type == "min":
            return min(result_u_to_lca, result_v_to_lca)
    
    def _query_up(self, node, ancestor, query_type):
        """
        Query the path from 'node' up to 'ancestor'.
        
        We move up chain by chain until we reach the ancestor.
        """
        result = 0 if query_type == "sum" else self.values[node]
        
        while self.chain_head[node] != self.chain_head[ancestor]:
            # Query from node to the head of its current chain
            chain_result = self._query_chain(self.chain_head[node], node, query_type)
            
            # Combine with overall result
            if query_type == "sum":
                result += chain_result
            elif query_type == "max":
                result = max(result, chain_result)
            elif query_type == "min":
                result = min(result, chain_result)
            
            # Move to parent of chain head (this is a light edge)
            node = self.parent[self.chain_head[node]]
        
        # Query the final segment within the same chain as ancestor
        if query_type == "sum":
            result += self._query_chain(ancestor, node, query_type)
        else:
            chain_result = self._query_chain(ancestor, node, query_type)
            result = max(result, chain_result) if query_type == "max" else min(result, chain_result)
        
        return result
    
    def _query_chain(self, u, v, query_type):
        """
        Query a segment within a single chain.
        
        In a real implementation, this would use a segment tree.
        Here we just iterate through the range for simplicity.
        """
        # Ensure u is higher in the tree than v
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        
        result = 0 if query_type == "sum" else self.values[u]
        
        # Simple iteration - in practice, use segment tree here
        current = u
        while current != v:
            if query_type == "sum":
                result += self.values[current]
            elif query_type == "max":
                result = max(result, self.values[current])
            elif query_type == "min":
                result = min(result, self.values[current])
            
            # Move to next node in chain (always the heavy child)
            if self.heavy_child[current] != -1 and self.depth[self.heavy_child[current]] <= self.depth[v]:
                current = self.heavy_child[current]
            else:
                break
        
        # Include the final node
        if query_type == "sum":
            result += self.values[v]
        elif query_type == "max":
            result = max(result, self.values[v])
        elif query_type == "min":
            result = min(result, self.values[v])
        
        return result
    
    def update_node(self, node, value):
        """Update the value of a single node."""
        self.values[node] = value
    
    def print_decomposition(self):
        """Print the decomposition info for debugging."""
        print("Heavy-Light Decomposition:")
        print(f"Number of chains: {self.chain_count}")
        
        for i in range(self.n):
            print(f"Node {i}: parent={self.parent[i]}, depth={self.depth[i]}, "
                  f"subtree_size={self.subtree_size[i]}, heavy_child={self.heavy_child[i]}, "
                  f"chain_head={self.chain_head[i]}, chain_pos={self.chain_pos[i]}")


# Example usage and testing
def example_usage():
    """
    Example of how to use Heavy-Light Decomposition.
    
    We'll create a simple tree and demonstrate path queries.
    """
    # Create a tree with 7 nodes
    #       0
    #      / \
    #     1   2
    #    /|   |\
    #   3 4   5 6
    
    hld = HeavyLightDecomposition(7)
    
    # Add edges
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    for u, v in edges:
        hld.add_edge(u, v)
    
    # Set some node values
    values = [10, 20, 30, 5, 15, 25, 35]
    for i, val in enumerate(values):
        hld.update_node(i, val)
    
    # Build the decomposition
    hld.build(root=0)
    
    # Print decomposition info
    hld.print_decomposition()
    
    print("\nPath Queries:")
    # Query sum from node 3 to node 6
    path_sum = hld.path_query(3, 6, "sum")
    print(f"Sum on path from 3 to 6: {path_sum}")
    # Expected: 5 + 20 + 10 + 30 + 35 = 100
    
    # Query max from node 4 to node 5
    path_max = hld.path_query(4, 5, "max")
    print(f"Max on path from 4 to 5: {path_max}")
    # Expected: max(15, 20, 10, 30, 25) = 30
    
    # Find LCA
    lca_result = hld.lca(3, 6)
    print(f"LCA of nodes 3 and 6: {lca_result}")
    # Expected: 0


if __name__ == "__main__":
    example_usage()
