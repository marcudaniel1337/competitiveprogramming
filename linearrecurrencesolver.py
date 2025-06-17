import numpy as np
from typing import List, Union, Tuple

class LinearRecurrenceSolver:
    """
    A solver for linear recurrence relations using matrix exponentiation.
    
    This class can solve recurrences of the form:
    a(n) = c1*a(n-1) + c2*a(n-2) + ... + ck*a(n-k)
    
    The key insight is that we can represent this as a matrix equation:
    [a(n), a(n-1), ..., a(n-k+1)] = [a(n-1), a(n-2), ..., a(n-k)] * M
    
    Where M is our transition matrix. Then a(n) = initial_state * M^(n-k)
    """
    
    def __init__(self, coefficients: List[float], initial_values: List[float]):
        """
        Initialize the recurrence solver.
        
        Args:
            coefficients: The coefficients [c1, c2, ..., ck] where
                         a(n) = c1*a(n-1) + c2*a(n-2) + ... + ck*a(n-k)
            initial_values: The first k values [a(0), a(1), ..., a(k-1)]
        
        Example:
            For Fibonacci: a(n) = a(n-1) + a(n-2), a(0)=0, a(1)=1
            coefficients = [1, 1], initial_values = [0, 1]
        """
        if len(coefficients) != len(initial_values):
            raise ValueError("Number of coefficients must match number of initial values")
        
        self.coefficients = np.array(coefficients, dtype=float)
        self.initial_values = np.array(initial_values, dtype=float)
        self.k = len(coefficients)  # Order of the recurrence
        
        # Build the transition matrix
        # This is the clever part - we create a matrix that shifts our state vector
        # and applies the recurrence relation
        self.transition_matrix = self._build_transition_matrix()
    
    def _build_transition_matrix(self) -> np.ndarray:
        """
        Build the transition matrix for the recurrence relation.
        
        The matrix looks like:
        [c1  c2  c3  ... ck ]
        [1   0   0   ... 0  ]
        [0   1   0   ... 0  ]
        [0   0   1   ... 0  ]
        ...
        [0   0   0   ... 0  ]
        
        The first row applies the recurrence relation.
        The other rows just shift the previous values down.
        """
        matrix = np.zeros((self.k, self.k))
        
        # First row: the recurrence coefficients
        matrix[0, :] = self.coefficients
        
        # Remaining rows: identity matrix shifted down
        # This creates the "memory" effect - keeping track of previous values
        for i in range(1, self.k):
            matrix[i, i-1] = 1
        
        return matrix
    
    def matrix_power(self, matrix: np.ndarray, n: int) -> np.ndarray:
        """
        Compute matrix^n using fast exponentiation (binary exponentiation).
        
        This is the secret sauce that makes everything fast!
        Instead of multiplying the matrix n times (O(n) operations),
        we use the fact that:
        - If n is even: matrix^n = (matrix^2)^(n/2)
        - If n is odd: matrix^n = matrix * matrix^(n-1)
        
        This reduces the complexity from O(n) to O(log n).
        """
        if n == 0:
            return np.eye(matrix.shape[0])  # Identity matrix
        
        if n == 1:
            return matrix.copy()
        
        # The recursive magic happens here
        if n % 2 == 0:
            # Even power: square the matrix and halve the exponent
            half_power = self.matrix_power(matrix, n // 2)
            return half_power @ half_power
        else:
            # Odd power: multiply by matrix and reduce exponent by 1
            return matrix @ self.matrix_power(matrix, n - 1)
    
    def solve(self, n: int) -> float:
        """
        Solve for the nth term of the recurrence relation.
        
        Args:
            n: The term number to compute (0-indexed)
            
        Returns:
            The value of a(n)
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        
        # Base case: if n is within our initial values, just return it
        if n < self.k:
            return self.initial_values[n]
        
        # The main algorithm:
        # We want to compute the state after (n - k + 1) steps
        # Our initial state is [a(k-1), a(k-2), ..., a(0)]
        # After applying the transition matrix (n - k + 1) times,
        # the first element will be a(n)
        
        steps = n - self.k + 1
        
        # Create initial state vector (most recent values first)
        initial_state = np.flip(self.initial_values)
        
        # Compute the transition matrix raised to the power of steps
        # This is where the logarithmic speedup happens!
        transition_power = self.matrix_power(self.transition_matrix, steps)
        
        # Apply the transition to our initial state
        final_state = initial_state @ transition_power
        
        # The first element of the final state is our answer
        return final_state[0]
    
    def solve_sequence(self, start: int, end: int) -> List[float]:
        """
        Solve for a range of terms efficiently.
        
        Args:
            start: Starting term number (inclusive)
            end: Ending term number (inclusive)
            
        Returns:
            List of values [a(start), a(start+1), ..., a(end)]
        """
        if start > end:
            return []
        
        # For small ranges, it might be faster to compute iteratively
        # But for large ranges or when start is large, matrix exponentiation wins
        
        return [self.solve(i) for i in range(start, end + 1)]
    
    def get_characteristic_polynomial(self) -> np.ndarray:
        """
        Get the characteristic polynomial of the recurrence relation.
        
        For a recurrence a(n) = c1*a(n-1) + c2*a(n-2) + ... + ck*a(n-k),
        the characteristic polynomial is:
        x^k - c1*x^(k-1) - c2*x^(k-2) - ... - ck = 0
        
        Returns:
            Coefficients of the characteristic polynomial (highest degree first)
        """
        # Start with x^k (coefficient 1 for x^k)
        poly = np.zeros(self.k + 1)
        poly[0] = 1
        
        # Subtract the recurrence coefficients
        for i, coeff in enumerate(self.coefficients):
            poly[i + 1] = -coeff
        
        return poly


# Example usage and demonstrations
def fibonacci_example():
    """Demonstrate solving Fibonacci sequence: F(n) = F(n-1) + F(n-2)"""
    print("=== Fibonacci Sequence Example ===")
    
    # F(n) = 1*F(n-1) + 1*F(n-2), with F(0)=0, F(1)=1
    fib_solver = LinearRecurrenceSolver([1, 1], [0, 1])
    
    print("First 20 Fibonacci numbers:")
    for i in range(20):
        print(f"F({i}) = {fib_solver.solve(i):.0f}")
    
    # Show the power of matrix exponentiation for large n
    print(f"\nF(100) = {fib_solver.solve(100):.0f}")
    print(f"F(1000) = {fib_solver.solve(1000):.2e}")
    
    return fib_solver

def tribonacci_example():
    """Demonstrate solving Tribonacci sequence: T(n) = T(n-1) + T(n-2) + T(n-3)"""
    print("\n=== Tribonacci Sequence Example ===")
    
    # T(n) = 1*T(n-1) + 1*T(n-2) + 1*T(n-3), with T(0)=0, T(1)=0, T(2)=1
    trib_solver = LinearRecurrenceSolver([1, 1, 1], [0, 0, 1])
    
    print("First 15 Tribonacci numbers:")
    for i in range(15):
        print(f"T({i}) = {trib_solver.solve(i):.0f}")
    
    return trib_solver

def custom_recurrence_example():
    """Demonstrate a custom recurrence relation"""
    print("\n=== Custom Recurrence Example ===")
    print("Solving: a(n) = 2*a(n-1) + 3*a(n-2) - a(n-3)")
    print("With initial values: a(0)=1, a(1)=2, a(2)=3")
    
    custom_solver = LinearRecurrenceSolver([2, 3, -1], [1, 2, 3])
    
    print("First 10 terms:")
    for i in range(10):
        print(f"a({i}) = {custom_solver.solve(i):.0f}")
    
    return custom_solver

def performance_comparison():
    """Compare the performance of matrix exponentiation vs naive computation"""
    print("\n=== Performance Comparison ===")
    
    import time
    
    # Create a Fibonacci solver
    fib_solver = LinearRecurrenceSolver([1, 1], [0, 1])
    
    # Test large n values
    test_values = [1000, 5000, 10000]
    
    for n in test_values:
        start_time = time.time()
        result = fib_solver.solve(n)
        end_time = time.time()
        
        print(f"F({n}) computed in {end_time - start_time:.6f} seconds")
        print(f"Result: {result:.2e}")
        print()

if __name__ == "__main__":
    # Run all examples
    fibonacci_example()
    tribonacci_example()
    custom_recurrence_example()
    performance_comparison()
    
    # Bonus: Show how to analyze the recurrence mathematically
    print("\n=== Mathematical Analysis ===")
    fib_solver = LinearRecurrenceSolver([1, 1], [0, 1])
    char_poly = fib_solver.get_characteristic_polynomial()
    print(f"Fibonacci characteristic polynomial coefficients: {char_poly}")
    print("This represents: x² - x - 1 = 0")
    
    # Find the roots (golden ratio and its conjugate)
    roots = np.roots(char_poly)
    print(f"Characteristic roots: {roots}")
    print(f"Golden ratio φ = {roots[0]:.6f}")
    print(f"Conjugate = {roots[1]:.6f}")
