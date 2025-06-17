import heapq
from collections import defaultdict, deque
import math

class MinCostFlow:
    def __init__(self):
        """
        Initialize our minimum cost flow solver.
        Think of this as setting up a logistics company - we need to track
        all our routes, capacities, and costs before we can start shipping.
        """
        # Our network is represented as an adjacency list
        # Each edge stores: [to_node, capacity, cost, flow, reverse_edge_index]
        self.graph = defaultdict(list)
        self.num_nodes = 0
    
    def add_edge(self, from_node, to_node, capacity, cost):
        """
        Add a shipping route between two locations.
        
        Think of this like adding a new truck route:
        - from_node: where we're shipping from
        - to_node: where we're shipping to  
        - capacity: how much we can ship on this route
        - cost: how much it costs per unit to use this route
        
        We also add a reverse edge with 0 capacity - this is like having
        a return route that we might use if we need to "undo" some flow later.
        """
        # Keep track of the highest node number we've seen
        self.num_nodes = max(self.num_nodes, from_node + 1, to_node + 1)
        
        # Add the forward edge
        forward_edge = [to_node, capacity, cost, 0, len(self.graph[to_node])]
        self.graph[from_node].append(forward_edge)
        
        # Add the reverse edge (starts with 0 capacity, negative cost)
        # This reverse edge is crucial for the algorithm to work correctly
        reverse_edge = [from_node, 0, -cost, 0, len(self.graph[from_node]) - 1]
        self.graph[to_node].append(reverse_edge)
    
    def shortest_path_spfa(self, source, sink, supply):
        """
        Find the cheapest path from source to sink using SPFA algorithm.
        
        SPFA (Shortest Path Faster Algorithm) is like having a smart GPS
        that not only finds paths but also keeps updating when it finds
        cheaper routes. It's particularly good at handling negative costs
        that can appear in our residual network.
        
        Returns: (distance, parent_info) where parent_info helps us reconstruct the path
        """
        # Initialize distances - start with "infinitely expensive" paths
        dist = [float('inf')] * self.num_nodes
        dist[source] = 0
        
        # Keep track of how we got to each node (for path reconstruction)
        parent = [-1] * self.num_nodes
        parent_edge = [-1] * self.num_nodes
        
        # Track which nodes are currently in our queue (avoid duplicates)
        in_queue = [False] * self.num_nodes
        
        # Start our search from the source
        queue = deque([source])
        in_queue[source] = True
        
        while queue:
            current = queue.popleft()
            in_queue[current] = False
            
            # Look at all outgoing routes from current location
            for edge_idx, edge in enumerate(self.graph[current]):
                neighbor, capacity, cost, flow, _ = edge
                
                # Can we actually ship anything on this route?
                # (Is there remaining capacity?)
                remaining_capacity = capacity - flow
                if remaining_capacity <= 0:
                    continue
                
                # Would using this route give us a cheaper path to the neighbor?
                new_cost = dist[current] + cost
                if new_cost < dist[neighbor]:
                    dist[neighbor] = new_cost
                    parent[neighbor] = current
                    parent_edge[neighbor] = edge_idx
                    
                    # Add neighbor to queue if it's not already there
                    if not in_queue[neighbor]:
                        queue.append(neighbor)
                        in_queue[neighbor] = True
        
        # If we can't reach the sink, there's no path available
        if dist[sink] == float('inf'):
            return None, None
        
        return dist[sink], (parent, parent_edge)
    
    def find_augmenting_path(self, source, sink):
        """
        Find a path where we can push more flow from source to sink.
        
        This is like finding a shipping route where we still have truck capacity
        available. We want the cheapest such route.
        """
        cost_per_unit, path_info = self.shortest_path_spfa(source, sink, 1)
        
        if path_info is None:
            return None, None, None
        
        parent, parent_edge = path_info
        
        # Reconstruct the path by following parent pointers backwards
        path = []
        current = sink
        min_capacity = float('inf')
        
        # Walk backwards from sink to source
        while parent[current] != -1:
            prev_node = parent[current]
            edge_idx = parent_edge[current]
            
            # Get the edge we used to reach current node
            edge = self.graph[prev_node][edge_idx]
            remaining_capacity = edge[1] - edge[3]  # capacity - flow
            
            # The bottleneck determines how much we can push through this path
            min_capacity = min(min_capacity, remaining_capacity)
            
            path.append((prev_node, current, edge_idx))
            current = prev_node
        
        # Reverse to get path from source to sink
        path.reverse()
        
        return path, min_capacity, cost_per_unit
    
    def push_flow_along_path(self, path, flow_amount):
        """
        Actually send the goods along our chosen route.
        
        This is like dispatching trucks along the path we've chosen.
        We need to update our records to show:
        1. Less capacity available on forward edges (trucks are using the route)
        2. More capacity on reverse edges (we could "recall" trucks if needed)
        """
        for from_node, to_node, edge_idx in path:
            # Update the forward edge (less capacity available)
            forward_edge = self.graph[from_node][edge_idx]
            forward_edge[3] += flow_amount  # increase flow
            
            # Update the corresponding reverse edge
            reverse_edge_idx = forward_edge[4]
            reverse_edge = self.graph[to_node][reverse_edge_idx]
            reverse_edge[3] -= flow_amount  # decrease flow (increase available capacity)
    
    def min_cost_flow(self, source, sink, max_flow_needed):
        """
        Solve the minimum cost flow problem using successive shortest paths.
        
        The idea is simple but powerful:
        1. Keep finding the cheapest path from source to sink
        2. Push as much flow as possible through that path
        3. Repeat until we've moved all the flow we need
        
        It's like a shipping company that always chooses the cheapest available
        route for each shipment, updating their route costs as trucks get busy.
        """
        total_cost = 0
        total_flow = 0
        
        print(f"Starting minimum cost flow from node {source} to node {sink}")
        print(f"We need to ship {max_flow_needed} units total")
        
        iteration = 1
        
        while total_flow < max_flow_needed:
            # Find the cheapest path that still has capacity
            path, flow_capacity, cost_per_unit = self.find_augmenting_path(source, sink)
            
            if path is None:
                print(f"\nNo more paths available! We could only ship {total_flow} out of {max_flow_needed} units")
                break
            
            # We can't ship more than what's needed
            flow_to_push = min(flow_capacity, max_flow_needed - total_flow)
            
            print(f"\nIteration {iteration}:")
            print(f"Found path with capacity {flow_capacity}, cost per unit: {cost_per_unit}")
            print(f"Shipping {flow_to_push} units along this path")
            
            # Actually move the flow along this path
            self.push_flow_along_path(path, flow_to_push)
            
            # Update our totals
            path_cost = flow_to_push * cost_per_unit
            total_cost += path_cost
            total_flow += flow_to_push
            
            print(f"Path cost: {path_cost}, Total cost so far: {total_cost}")
            print(f"Total flow so far: {total_flow}")
            
            iteration += 1
        
        if total_flow == max_flow_needed:
            print(f"\nSuccess! Shipped all {max_flow_needed} units")
            print(f"Total minimum cost: {total_cost}")
        
        return total_flow, total_cost
    
    def print_final_flows(self):
        """
        Show the final shipping schedule - which routes are being used
        and how much is being shipped on each route.
        """
        print("\nFinal shipping schedule:")
        print("Route (from -> to): Flow/Capacity at Cost per unit")
        
        for from_node in self.graph:
            for edge in self.graph[from_node]:
                to_node, capacity, cost, flow, _ = edge
                if flow > 0:  # Only show routes that are actually being used
                    print(f"Route {from_node} -> {to_node}: {flow}/{capacity} at cost {cost} per unit")


# Example usage and testing
def example_transportation_problem():
    """
    Solve a classic transportation problem:
    
    We have 2 factories that produce goods and 2 warehouses that need goods.
    Factory 0 can produce 20 units, Factory 1 can produce 30 units.
    Warehouse 2 needs 25 units, Warehouse 3 needs 25 units.
    
    The shipping costs per unit are:
    Factory 0 -> Warehouse 2: $4 per unit
    Factory 0 -> Warehouse 3: $6 per unit  
    Factory 1 -> Warehouse 2: $3 per unit
    Factory 1 -> Warehouse 3: $2 per unit
    
    We want to find the cheapest way to satisfy all warehouse demands.
    """
    print("="*60)
    print("TRANSPORTATION PROBLEM EXAMPLE")
    print("="*60)
    
    mcf = MinCostFlow()
    
    # We'll use a super-source (node 4) and super-sink (node 5)
    # to convert this into a single-source single-sink problem
    
    # Connect super-source to factories (supply edges)
    mcf.add_edge(4, 0, 20, 0)  # Factory 0 can supply 20 units at no cost
    mcf.add_edge(4, 1, 30, 0)  # Factory 1 can supply 30 units at no cost
    
    # Connect factories to warehouses (transportation edges)
    mcf.add_edge(0, 2, 50, 4)  # Factory 0 -> Warehouse 2: $4 per unit
    mcf.add_edge(0, 3, 50, 6)  # Factory 0 -> Warehouse 3: $6 per unit
    mcf.add_edge(1, 2, 50, 3)  # Factory 1 -> Warehouse 2: $3 per unit
    mcf.add_edge(1, 3, 50, 2)  # Factory 1 -> Warehouse 3: $2 per unit
    
    # Connect warehouses to super-sink (demand edges)
    mcf.add_edge(2, 5, 25, 0)  # Warehouse 2 needs 25 units
    mcf.add_edge(3, 5, 25, 0)  # Warehouse 3 needs 25 units
    
    # Solve the problem
    total_flow, total_cost = mcf.min_cost_flow(4, 5, 50)
    
    # Show the results
    mcf.print_final_flows()
    
    return total_flow, total_cost


def example_simple_network():
    """
    A simpler example to understand the algorithm:
    
    Node 0 has 10 units to send to Node 3
    There are multiple paths with different costs:
    - Direct path: 0->3 (cost 10 per unit, capacity 5)
    - Via node 1: 0->1->3 (costs 2+3=5 per unit, capacity 8 each)
    - Via node 2: 0->2->3 (costs 4+1=5 per unit, capacity 6 each)
    """
    print("\n" + "="*60)
    print("SIMPLE NETWORK EXAMPLE")
    print("="*60)
    
    mcf = MinCostFlow()
    
    # Add edges: from, to, capacity, cost
    mcf.add_edge(0, 3, 5, 10)   # Direct route: expensive but available
    mcf.add_edge(0, 1, 8, 2)    # Route via node 1: cheaper
    mcf.add_edge(1, 3, 8, 3)
    mcf.add_edge(0, 2, 6, 4)    # Route via node 2: also cheaper  
    mcf.add_edge(2, 3, 6, 1)
    
    # Try to send 10 units from node 0 to node 3
    total_flow, total_cost = mcf.min_cost_flow(0, 3, 10)
    
    mcf.print_final_flows()
    
    return total_flow, total_cost


if __name__ == "__main__":
    # Run our examples
    example_simple_network()
    example_transportation_problem()
    
    print("\n" + "="*60)
    print("ALGORITHM SUMMARY")
    print("="*60)
    print("The Successive Shortest Path algorithm works by:")
    print("1. Finding the cheapest path from source to sink")
    print("2. Pushing maximum possible flow along that path")  
    print("3. Updating the residual network")
    print("4. Repeating until no more flow can be sent")
    print("\nThis guarantees we find the minimum cost way to send the required flow!")
