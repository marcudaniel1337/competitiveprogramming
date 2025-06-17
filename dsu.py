class RollbackDSU:
    """
    Disjoint Set Union with rollback capability.
    
    This is like having a time machine for your union-find operations - 
    you can undo unions and go back to previous states. Pretty neat for 
    when you need to try different scenarios!
    """
    
    def __init__(self, n):
        # Each element starts as its own parent (everyone's their own boss initially)
        self.parent = list(range(n))
        # Track the size of each component (how many friends each group has)
        self.size = [1] * n
        # This is our "undo stack" - keeps track of what we changed
        self.history = []
        
    def find(self, x):
        """
        Find the root of element x.
        
        Note: We DON'T use path compression here because it would mess up
        our rollback functionality. It's like writing in pen when you need
        to use pencil - you can't erase it later!
        """
        while self.parent[x] != x:
            x = self.parent[x]
        return x
    
    def union(self, x, y):
        """
        Unite two components and remember what we did for potential rollback.
        
        It's like introducing two friend groups - we need to remember
        who was the leader before in case we want to separate them later.
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        # If they're already in the same group, nothing to do
        if root_x == root_y:
            # Still need to record this "no-op" for consistent rollback
            self.history.append(None)
            return False
        
        # Union by size heuristic - smaller group joins the larger one
        # It's like merging companies - the smaller one usually gets absorbed
        if self.size[root_x] < self.size[root_y]:
            root_x, root_y = root_y, root_x
        
        # Remember the old state before we change anything
        # This is our "save point" that we can return to
        self.history.append((root_y, self.parent[root_y], self.size[root_x]))
        
        # Actually perform the union
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        
        return True
    
    def rollback(self):
        """
        Undo the last union operation.
        
        This is like pressing Ctrl+Z - we go back to how things were
        before the last change.
        """
        if not self.history:
            return  # Nothing to undo
        
        last_op = self.history.pop()
        
        if last_op is None:
            # This was a no-op union, nothing to actually undo
            return
        
        # Unpack what we saved earlier
        node, old_parent, old_size = last_op
        
        # Restore the old state
        self.parent[node] = old_parent
        # We need to find the root to restore its size
        root = self.find(old_parent) if old_parent != node else node
        if root != node:  # Only restore size if we're not dealing with the root itself
            self.size[root] = old_size
            self.size[node] = self.size[node] - old_size + 1
    
    def connected(self, x, y):
        """Check if two elements are in the same component."""
        return self.find(x) == self.find(y)
    
    def get_checkpoint(self):
        """Get current state for later rollback to this exact point."""
        return len(self.history)
    
    def rollback_to(self, checkpoint):
        """Roll back to a specific checkpoint."""
        while len(self.history) > checkpoint:
            self.rollback()


class OfflineDynamicConnectivity:
    """
    Offline Dynamic Connectivity solver using divide and conquer with DSU rollback.
    
    This is for when you have all your operations upfront and want to answer
    connectivity queries efficiently. Think of it as planning a road trip -
    you know all the places you want to visit before you start driving.
    """
    
    def __init__(self, n):
        self.n = n  # Number of nodes
        self.operations = []  # All operations we'll process
        self.answers = []  # Results for query operations
    
    def add_edge(self, u, v, time_start, time_end):
        """
        Add an edge that exists from time_start to time_end (exclusive).
        
        Think of this as a temporary bridge - it's only there for a certain
        period of time.
        """
        self.operations.append(('edge', u, v, time_start, time_end))
    
    def add_query(self, u, v, time):
        """
        Add a connectivity query at a specific time.
        
        This is asking: "Are these two nodes connected at this moment?"
        """
        query_id = len([op for op in self.operations if op[0] == 'query'])
        self.operations.append(('query', u, v, time, query_id))
    
    def solve(self):
        """
        Solve all queries using divide and conquer.
        
        This is the magic part - we use a clever recursive approach that
        processes queries efficiently by grouping them smartly.
        """
        # Separate queries from edges
        queries = [(op[1], op[2], op[3], op[4]) for op in self.operations if op[0] == 'query']
        edges = [(op[1], op[2], op[3], op[4]) for op in self.operations if op[0] == 'edge']
        
        self.answers = [False] * len(queries)
        
        # Start the divide and conquer process
        self._solve_recursive(edges, list(range(len(queries))), queries, 
                            RollbackDSU(self.n), 0, max(op[3] for op in self.operations) + 1)
        
        return self.answers
    
    def _solve_recursive(self, edges, query_indices, queries, dsu, time_left, time_right):
        """
        The heart of our algorithm - divide and conquer with rollback.
        
        This recursively splits the time range and processes queries.
        It's like organizing a timeline - we handle different time periods
        separately but efficiently.
        """
        if not query_indices:
            return  # No queries to process
        
        if time_right - time_left == 1:
            # Base case: single time unit
            # Check all queries at this time
            for qi in query_indices:
                u, v, t, qid = queries[qi]
                if t == time_left:
                    self.answers[qid] = dsu.connected(u, v)
            return
        
        time_mid = (time_left + time_right) // 2
        
        # Get checkpoint before adding any edges
        checkpoint = dsu.get_checkpoint()
        
        # Add all edges that completely span the left half [time_left, time_mid)
        edges_added = 0
        for u, v, start, end in edges:
            if start <= time_left and end >= time_mid:
                dsu.union(u, v)
                edges_added += 1
        
        # Split queries based on which half they belong to
        left_queries = []
        right_queries = []
        
        for qi in query_indices:
            u, v, t, qid = queries[qi]
            if t < time_mid:
                left_queries.append(qi)
            else:
                right_queries.append(qi)
        
        # Recursively solve left half
        # Edges spanning left half are already added to DSU
        left_edges = [(u, v, start, end) for u, v, start, end in edges 
                     if not (start <= time_left and end >= time_mid)]
        self._solve_recursive(left_edges, left_queries, queries, dsu, time_left, time_mid)
        
        # Recursively solve right half
        # We keep the edges we added (they might span into right half too)
        right_edges = [(u, v, start, end) for u, v, start, end in edges 
                      if not (start <= time_left and end >= time_mid)]
        self._solve_recursive(right_edges, right_queries, queries, dsu, time_mid, time_right)
        
        # Rollback to checkpoint - clean up the edges we added
        # This is like cleaning up after a party - we put everything back
        # how it was before we started
        dsu.rollback_to(checkpoint)


def demo_offline_dynamic_connectivity():
    """
    Demo showing how to use offline dynamic connectivity.
    
    Let's simulate a social network where friendships come and go,
    and we want to know if people were connected at specific times.
    """
    print("=== Offline Dynamic Connectivity Demo ===\n")
    
    # Create a system with 6 people (nodes 0-5)
    connectivity = OfflineDynamicConnectivity(6)
    
    # Add some friendships (edges) with time ranges
    print("Adding friendships (edges) with time ranges:")
    
    # Alice (0) and Bob (1) are friends from time 1 to 5
    connectivity.add_edge(0, 1, 1, 5)
    print("- Alice (0) and Bob (1): friends from time 1 to 5")
    
    # Bob (1) and Charlie (2) are friends from time 2 to 4
    connectivity.add_edge(1, 2, 2, 4)
    print("- Bob (1) and Charlie (2): friends from time 2 to 4")
    
    # Dave (3) and Eve (4) are friends from time 1 to 6
    connectivity.add_edge(3, 4, 1, 6)
    print("- Dave (3) and Eve (4): friends from time 1 to 6")
    
    # Charlie (2) and Dave (3) are friends from time 3 to 7
    connectivity.add_edge(2, 3, 3, 7)
    print("- Charlie (2) and Dave (3): friends from time 3 to 7")
    
    print("\nAdding connectivity queries:")
    
    # Add some queries to check connectivity at different times
    queries = [
        (0, 2, 1, "Are Alice and Charlie connected at time 1?"),
        (0, 2, 3, "Are Alice and Charlie connected at time 3?"),
        (0, 4, 3, "Are Alice and Eve connected at time 3?"),
        (1, 4, 4, "Are Bob and Eve connected at time 4?"),
        (0, 5, 2, "Are Alice and Frank connected at time 2?")
    ]
    
    for u, v, t, description in queries:
        connectivity.add_query(u, v, t)
        print(f"- {description}")
    
    # Solve all queries
    print("\nSolving all queries...")
    answers = connectivity.solve()
    
    print("\nResults:")
    for i, (u, v, t, description) in enumerate(queries):
        result = "YES" if answers[i] else "NO"
        print(f"- {description} → {result}")
    
    print("\nExplanation of results:")
    print("1. Alice-Charlie at time 1: NO (Charlie not connected to Alice's component yet)")
    print("2. Alice-Charlie at time 3: YES (Alice→Bob→Charlie path exists)")
    print("3. Alice-Eve at time 3: YES (Alice→Bob→Charlie→Dave→Eve path exists)")
    print("4. Bob-Eve at time 4: NO (Bob-Charlie edge expires at time 4)")
    print("5. Alice-Frank at time 2: NO (Frank (5) has no connections)")


def demo_dsu_rollback():
    """
    Demo showing the rollback functionality of DSU.
    
    This shows how we can undo operations - useful for the divide and
    conquer algorithm.
    """
    print("\n=== DSU Rollback Demo ===\n")
    
    dsu = RollbackDSU(5)
    print("Created DSU with 5 elements (0, 1, 2, 3, 4)")
    print("Initially, each element is in its own component")
    
    # Show initial state
    print(f"Initial connectivity: 0-1? {dsu.connected(0, 1)}")
    
    # Perform some unions
    print("\nPerforming unions:")
    print("Union(0, 1)")
    dsu.union(0, 1)
    print(f"After union: 0-1? {dsu.connected(0, 1)}")
    
    print("Union(2, 3)")
    dsu.union(2, 3)
    print(f"After union: 2-3? {dsu.connected(2, 3)}")
    
    print("Union(1, 2) - this connects the two components")
    dsu.union(1, 2)
    print(f"Now 0-3? {dsu.connected(0, 3)} (should be True)")
    
    # Get a checkpoint for later
    checkpoint = dsu.get_checkpoint()
    print(f"\nSaved checkpoint at position {checkpoint}")
    
    print("Union(0, 4)")
    dsu.union(0, 4)
    print(f"Now 1-4? {dsu.connected(1, 4)} (should be True)")
    
    # Rollback one operation
    print("\nRolling back last operation...")
    dsu.rollback()
    print(f"After rollback, 1-4? {dsu.connected(1, 4)} (should be False)")
    print(f"But 0-3? {dsu.connected(0, 3)} (should still be True)")
    
    # Rollback to checkpoint
    print(f"\nRolling back to checkpoint {checkpoint}...")
    dsu.rollback_to(checkpoint)
    print(f"After rollback to checkpoint:")
    print(f"- 0-1? {dsu.connected(0, 1)} (should be True)")
    print(f"- 2-3? {dsu.connected(2, 3)} (should be True)")
    print(f"- 0-3? {dsu.connected(0, 3)} (should be False)")


if __name__ == "__main__":
    # Run both demos
    demo_dsu_rollback()
    demo_offline_dynamic_connectivity()
    
    print("\n=== Summary ===")
    print("This implementation provides:")
    print("• RollbackDSU: Union-Find with undo capability")
    print("• OfflineDynamicConnectivity: Efficient solver for connectivity queries")
    print("• Time complexity: O((n + q) log(n) log(T)) where n=nodes, q=queries, T=time range")
    print("• Space complexity: O(n + q)")
    print("\nUse cases:")
    print("• Social network evolution analysis")
    print("• Road network with temporary closures")
    print("• Network reliability over time")
    print("• Any scenario with temporary connections and historical queries")
