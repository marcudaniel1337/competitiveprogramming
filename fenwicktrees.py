class BinaryIndexedTree2D:
    """
    A 2D Binary Indexed Tree (also known as 2D Fenwick Tree) for efficient
    range sum queries and point updates on a 2D matrix.
    
    Think of this as a clever way to store partial sums that allows us to:
    - Update any single element in O(log n * log m) time
    - Query the sum of any rectangle in O(log n * log m) time
    
    The magic happens because we store sums in a tree-like structure where
    each node represents the sum of a specific rectangular region.
    """
    
    def __init__(self, rows, cols):
        """
        Initialize our 2D BIT with the given dimensions.
        
        We need rows+1 and cols+1 because BIT uses 1-based indexing internally.
        This makes the bit manipulation math work out nicely - when we do
        operations like i & -i, we want to avoid issues with index 0.
        """
        self.rows = rows
        self.cols = cols
        # Create a 2D array filled with zeros - this will store our tree
        self.tree = [[0] * (cols + 1) for _ in range(rows + 1)]
    
    def update(self, row, col, delta):
        """
        Add 'delta' to the element at position (row, col).
        
        The beauty of BIT is that when we update one element, we only need
        to update O(log n * log m) nodes in our tree structure. We do this
        by moving through the tree using bit manipulation.
        
        For each row, we update all columns that this position affects.
        The pattern i += i & -i moves us to the next position that needs updating.
        
        Think of i & -i as "what's the rightmost bit that's set in i?"
        Adding this to i effectively moves us up the tree to the parent node.
        """
        # Convert to 1-based indexing for internal calculations
        row += 1
        col += 1
        
        # Start from our target row and work our way up the tree
        r = row
        while r <= self.rows:
            # For this row, update all relevant columns
            c = col
            while c <= self.cols:
                self.tree[r][c] += delta
                # Move to the next column position that needs updating
                # This bit trick finds the next position up the column tree
                c += c & -c
            # Move to the next row position that needs updating
            r += r & -r
    
    def _query(self, row, col):
        """
        Get the sum of all elements from (0,0) to (row, col) inclusive.
        
        This is the core query operation. We sum up values from multiple
        nodes in our tree to get the total sum for the rectangle from
        the top-left corner to our query point.
        
        The pattern i -= i & -i moves us down the tree, visiting all
        the nodes whose ranges contribute to our final sum.
        """
        if row < 0 or col < 0:
            return 0
        
        # Convert to 1-based indexing
        row += 1
        col += 1
        
        total_sum = 0
        r = row
        while r > 0:
            c = col
            while c > 0:
                total_sum += self.tree[r][c]
                # Move to the previous column position in our tree traversal
                c -= c & -c
            # Move to the previous row position in our tree traversal
            r -= r & -r
        
        return total_sum
    
    def range_query(self, row1, col1, row2, col2):
        """
        Get the sum of elements in the rectangle defined by corners
        (row1, col1) and (row2, col2), both inclusive.
        
        This uses the inclusion-exclusion principle:
        - Start with the sum from (0,0) to (row2, col2)
        - Subtract the parts we don't want (the areas outside our rectangle)
        - Add back the part we subtracted twice (the overlap)
        
        It's like calculating the area of a rectangle by using bigger rectangles
        and subtracting the parts you don't need.
        """
        if row1 > row2 or col1 > col2:
            return 0
        
        # Get the sum of the large rectangle from origin to bottom-right
        total = self._query(row2, col2)
        
        # Subtract the rectangle above our target area
        if row1 > 0:
            total -= self._query(row1 - 1, col2)
        
        # Subtract the rectangle to the left of our target area
        if col1 > 0:
            total -= self._query(row2, col1 - 1)
        
        # Add back the rectangle we subtracted twice (top-left corner)
        if row1 > 0 and col1 > 0:
            total += self._query(row1 - 1, col1 - 1)
        
        return total
    
    def set_value(self, row, col, new_value):
        """
        Set the element at (row, col) to new_value.
        
        Since our BIT only supports adding deltas, we need to:
        1. Calculate what the current value is
        2. Find the difference between new and current value
        3. Apply that difference as an update
        
        Note: This requires us to track original values, which adds complexity.
        In practice, you might want to maintain a separate matrix for this.
        """
        # For simplicity, we'll implement this by getting current value
        # and applying the difference. In a real implementation, you'd
        # probably want to store the original matrix separately.
        current_value = self.range_query(row, col, row, col)
        delta = new_value - current_value
        self.update(row, col, delta)


def demonstrate_2d_bit():
    """
    Let's see our 2D BIT in action with some examples!
    This will help you understand how it works in practice.
    """
    print("Creating a 4x4 2D Binary Indexed Tree...")
    bit = BinaryIndexedTree2D(4, 4)
    
    print("\nInitial state: all zeros")
    for i in range(4):
        for j in range(4):
            print(f"{bit.range_query(i, j, i, j):3d}", end=" ")
        print()
    
    print("\nLet's add some values to our matrix...")
    # Add 5 to position (1, 1)
    bit.update(1, 1, 5)
    print("Added 5 to position (1,1)")
    
    # Add 3 to position (2, 2)
    bit.update(2, 2, 3)
    print("Added 3 to position (2,2)")
    
    # Add 7 to position (0, 3)
    bit.update(0, 3, 7)
    print("Added 7 to position (0,3)")
    
    print("\nCurrent matrix values:")
    for i in range(4):
        for j in range(4):
            print(f"{bit.range_query(i, j, i, j):3d}", end=" ")
        print()
    
    print("\nTesting range queries...")
    
    # Query sum of rectangle from (0,0) to (2,2)
    sum_rect = bit.range_query(0, 0, 2, 2)
    print(f"Sum of rectangle (0,0) to (2,2): {sum_rect}")
    
    # Query sum of rectangle from (1,1) to (2,2)
    sum_rect2 = bit.range_query(1, 1, 2, 2)
    print(f"Sum of rectangle (1,1) to (2,2): {sum_rect2}")
    
    # Query sum of first row
    sum_row = bit.range_query(0, 0, 0, 3)
    print(f"Sum of first row: {sum_row}")
    
    print("\nUpdating position (1,1) by adding 2 more...")
    bit.update(1, 1, 2)
    
    print("New matrix values:")
    for i in range(4):
        for j in range(4):
            print(f"{bit.range_query(i, j, i, j):3d}", end=" ")
        print()
    
    # Verify the sum changed correctly
    new_sum_rect2 = bit.range_query(1, 1, 2, 2)
    print(f"Sum of rectangle (1,1) to (2,2) after update: {new_sum_rect2}")


class Matrix2D:
    """
    A helper class that combines a regular 2D matrix with a BIT for efficient operations.
    This makes it easier to work with since you don't have to manually track original values.
    """
    
    def __init__(self, rows, cols, initial_matrix=None):
        """
        Create a matrix with BIT support.
        You can either start with all zeros or provide an initial matrix.
        """
        self.rows = rows
        self.cols = cols
        self.matrix = [[0] * cols for _ in range(rows)]
        self.bit = BinaryIndexedTree2D(rows, cols)
        
        # If we're given an initial matrix, set it up
        if initial_matrix:
            for i in range(rows):
                for j in range(cols):
                    if i < len(initial_matrix) and j < len(initial_matrix[i]):
                        value = initial_matrix[i][j]
                        self.matrix[i][j] = value
                        self.bit.update(i, j, value)
    
    def set(self, row, col, value):
        """Set a specific position to a value."""
        old_value = self.matrix[row][col]
        delta = value - old_value
        self.matrix[row][col] = value
        self.bit.update(row, col, delta)
    
    def get(self, row, col):
        """Get the value at a specific position."""
        return self.matrix[row][col]
    
    def add(self, row, col, delta):
        """Add a value to a specific position."""
        self.matrix[row][col] += delta
        self.bit.update(row, col, delta)
    
    def range_sum(self, row1, col1, row2, col2):
        """Get the sum of a rectangular region."""
        return self.bit.range_query(row1, col1, row2, col2)
    
    def print_matrix(self):
        """Print the current state of the matrix."""
        print("Current matrix:")
        for row in self.matrix:
            print([f"{x:3d}" for x in row])


def demonstrate_matrix2d():
    """
    Show how the Matrix2D class makes things even easier to use!
    """
    print("=== Matrix2D Demonstration ===")
    
    # Create a 3x3 matrix with some initial values
    initial = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    matrix = Matrix2D(3, 3, initial)
    matrix.print_matrix()
    
    print(f"\nSum of entire matrix: {matrix.range_sum(0, 0, 2, 2)}")
    print(f"Sum of top-left 2x2: {matrix.range_sum(0, 0, 1, 1)}")
    print(f"Sum of bottom-right 2x2: {matrix.range_sum(1, 1, 2, 2)}")
    
    print("\nSetting position (1,1) to 10...")
    matrix.set(1, 1, 10)
    matrix.print_matrix()
    
    print(f"New sum of top-left 2x2: {matrix.range_sum(0, 0, 1, 1)}")
    print(f"New sum of bottom-right 2x2: {matrix.range_sum(1, 1, 2, 2)}")
    
    print("\nAdding 5 to position (0,0)...")
    matrix.add(0, 0, 5)
    matrix.print_matrix()
    
    print(f"Final sum of entire matrix: {matrix.range_sum(0, 0, 2, 2)}")


if __name__ == "__main__":
    # Run our demonstrations
    demonstrate_2d_bit()
    print("\n" + "="*50 + "\n")
    demonstrate_matrix2d()
    
    print("\n" + "="*50)
    print("Time Complexity Summary:")
    print("- Update single element: O(log n * log m)")
    print("- Range sum query: O(log n * log m)")
    print("- Space complexity: O(n * m)")
    print("\nThis is much better than naive approaches which would be:")
    print("- Naive update: O(1), but range query: O(n * m)")
    print("- Or with prefix sums: update O(n * m), query O(1)")
    print("BIT gives us the best of both worlds!")
