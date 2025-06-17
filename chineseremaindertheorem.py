def extended_gcd(a, b):
    """
    The Extended Euclidean Algorithm - this is like the regular GCD but with superpowers!
    
    Regular GCD just finds the greatest common divisor, but this version also finds
    the coefficients (x, y) such that: a*x + b*y = gcd(a, b)
    
    Why do we need this? Because these coefficients are exactly what we need
    to find modular inverses, which are crucial for the Chinese Remainder Theorem.
    
    Think of it like solving: "I have some number of $5 bills and $7 bills that 
    add up to $1. How many of each do I need?" (when gcd(5,7) = 1)
    """
    if a == 0:
        # Base case: gcd(0, b) = b, and 0*0 + b*1 = b
        return b, 0, 1
    
    # Recursively apply the algorithm
    gcd, x1, y1 = extended_gcd(b % a, a)
    
    # Back-substitute to find our coefficients
    # This math comes from the Euclidean algorithm's steps in reverse
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Find the modular inverse of 'a' modulo 'm'.
    
    This answers: "What number, when multiplied by 'a', gives remainder 1 when divided by 'm'?"
    For example: mod_inverse(3, 7) = 5, because 3 * 5 = 15 ≡ 1 (mod 7)
    
    This only exists when gcd(a, m) = 1 (a and m are coprime).
    Think of it like finding the "undo" operation for multiplication in modular arithmetic.
    """
    gcd, x, y = extended_gcd(a, m)
    
    if gcd != 1:
        # No inverse exists - like trying to divide by zero in regular arithmetic
        raise ValueError(f"Modular inverse of {a} mod {m} doesn't exist (they're not coprime)")
    
    # x might be negative, so we add m to make it positive
    # This is like saying -2 ≡ 5 (mod 7)
    return (x % m + m) % m


def chinese_remainder_theorem(remainders, moduli):
    """
    Solve a system of congruences using the Chinese Remainder Theorem.
    
    Given equations like:
    x ≡ r1 (mod m1)
    x ≡ r2 (mod m2)
    x ≡ r3 (mod m3)
    ...
    
    Find the unique solution x modulo (m1 * m2 * m3 * ...)
    
    Real-world example: "I have some eggs. When I group them by 3, I have 2 left over.
    When I group by 5, I have 3 left over. When I group by 7, I have 2 left over.
    How many eggs do I have?" This would be solved with remainders=[2,3,2], moduli=[3,5,7]
    
    Args:
        remainders: List of remainders [r1, r2, r3, ...]
        moduli: List of moduli [m1, m2, m3, ...]
    
    Returns:
        The unique solution x in the range [0, product_of_all_moduli)
    """
    
    # First, let's validate our inputs
    if len(remainders) != len(moduli):
        raise ValueError("Need the same number of remainders and moduli!")
    
    if len(remainders) == 0:
        raise ValueError("Need at least one congruence to solve!")
    
    # Check that all moduli are pairwise coprime (gcd = 1 for every pair)
    # This is required for CRT to work - like making sure puzzle pieces don't overlap
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            gcd, _, _ = extended_gcd(moduli[i], moduli[j])
            if gcd != 1:
                raise ValueError(f"Moduli {moduli[i]} and {moduli[j]} are not coprime (gcd = {gcd}). CRT requires pairwise coprime moduli!")
    
    # Calculate the total product - this is our "universe size"
    # The final answer will be unique modulo this number
    total_product = 1
    for m in moduli:
        total_product *= m
    
    # This is where the magic happens!
    solution = 0
    
    for i in range(len(remainders)):
        # For each congruence x ≡ ri (mod mi), we need to:
        # 1. Find Mi = total_product / mi (product of all OTHER moduli)
        # 2. Find yi = inverse of Mi modulo mi
        # 3. Add ri * Mi * yi to our solution
        
        # Step 1: Mi is like a "weight" that's divisible by all moduli except mi
        Mi = total_product // moduli[i]
        
        # Step 2: We need Mi * yi ≡ 1 (mod mi)
        # This ensures our term contributes exactly ri when taken modulo mi
        yi = mod_inverse(Mi, moduli[i])
        
        # Step 3: Add this term to our solution
        # This term will be ≡ ri (mod mi) and ≡ 0 (mod mj) for all j ≠ i
        term = remainders[i] * Mi * yi
        solution += term
        
        # Optional: show the construction step by step
        print(f"Step {i+1}: For x ≡ {remainders[i]} (mod {moduli[i]})")
        print(f"  Mi = {total_product}/{moduli[i]} = {Mi}")
        print(f"  yi = inverse of {Mi} mod {moduli[i]} = {yi}")
        print(f"  Term = {remainders[i]} × {Mi} × {yi} = {term}")
        print(f"  Running solution = {solution}")
        print()
    
    # Reduce to the canonical range [0, total_product)
    final_solution = solution % total_product
    
    print(f"Final answer: x ≡ {final_solution} (mod {total_product})")
    return final_solution


def verify_solution(solution, remainders, moduli):
    """
    Double-check that our solution actually works.
    This is like checking your math homework - always a good idea!
    """
    print("Verification:")
    all_correct = True
    
    for i in range(len(remainders)):
        actual_remainder = solution % moduli[i]
        expected_remainder = remainders[i]
        
        is_correct = actual_remainder == expected_remainder
        status = "✓" if is_correct else "✗"
        
        print(f"  {solution} ≡ {actual_remainder} (mod {moduli[i]}) - Expected: {expected_remainder} {status}")
        
        if not is_correct:
            all_correct = False
    
    print(f"\nOverall result: {'All correct! 🎉' if all_correct else 'Something went wrong 😞'}")
    return all_correct


# Example usage and test cases
if __name__ == "__main__":
    print("=== Chinese Remainder Theorem Demo ===\n")
    
    # Classic textbook example
    print("Example 1: The classic egg problem")
    print("A farmer has some eggs. When grouped by 3, 2 remain. When grouped by 5, 3 remain. When grouped by 7, 2 remain.")
    print("How many eggs? (Looking for smallest positive answer)\n")
    
    remainders1 = [2, 3, 2]
    moduli1 = [3, 5, 7]
    
    try:
        solution1 = chinese_remainder_theorem(remainders1, moduli1)
        verify_solution(solution1, remainders1, moduli1)
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Another example
    print("Example 2: A more complex system")
    print("x ≡ 1 (mod 2)")
    print("x ≡ 2 (mod 3)")  
    print("x ≡ 3 (mod 5)")
    print("x ≡ 4 (mod 11)\n")
    
    remainders2 = [1, 2, 3, 4]
    moduli2 = [2, 3, 5, 11]
    
    try:
        solution2 = chinese_remainder_theorem(remainders2, moduli2)
        verify_solution(solution2, remainders2, moduli2)
    except ValueError as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example that should fail (non-coprime moduli)
    print("Example 3: What happens when moduli aren't coprime?")
    print("x ≡ 1 (mod 6)")
    print("x ≡ 2 (mod 9)")
    print("(Note: gcd(6,9) = 3, so this should fail)\n")
    
    remainders3 = [1, 2]
    moduli3 = [6, 9]
    
    try:
        solution3 = chinese_remainder_theorem(remainders3, moduli3)
        verify_solution(solution3, remainders3, moduli3)
    except ValueError as e:
        print(f"Error: {e}")
        print("This is expected! CRT only works when moduli are pairwise coprime.")
