import random
from typing import Optional, List, Tuple

class TreapNode:
    """
    A node in a Treap (Tree + Heap).
    
    The genius of treaps is combining BST property with heap property:
    - BST property: left.key < key < right.key (for searching)
    - Heap property: priority > left.priority and priority > right.priority (for balance)
    
    The random priorities ensure expected O(log n) height with high probability.
    It's like having a perfectly balanced tree without the complexity of rotations!
    """
    def __init__(self, key: int, value=None):
        self.key = key
        self.value = value if value is not None else key
        self.priority = random.random()  # Random priority is the magic sauce
        self.left: Optional['TreapNode'] = None
        self.right: Optional['TreapNode'] = None

class Treap:
    """
    Treap: The probabilistically balanced BST that's surprisingly simple.
    
    Why treaps are awesome:
    1. Expected O(log n) operations without complex balancing logic
    2. Easy to implement compared to deterministic balanced trees
    3. Excellent for scenarios where you need "good enough" balance
    4. The randomization makes worst-case scenarios extremely unlikely
    """
    
    def __init__(self):
        self.root: Optional[TreapNode] = None
    
    def _rotate_right(self, node: TreapNode) -> TreapNode:
        """
        Right rotation - think of it as lifting the left child up.
        
        Before:     After:
           y           x
          / \         / \
         x   C  -->  A   y
        / \             / \
       A   B           B   C
        
        We do this when left child has higher priority (heap property violation)
        """
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        return left_child
    
    def _rotate_left(self, node: TreapNode) -> TreapNode:
        """
        Left rotation - think of it as lifting the right child up.
        
        Before:     After:
           x           y
          / \         / \
         A   y  -->  x   C
            / \     / \
           B   C   A   B
        
        We do this when right child has higher priority (heap property violation)
        """
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        return right_child
    
    def insert(self, key: int, value=None) -> None:
        """Insert a key-value pair. The magic happens in the recursive helper."""
        self.root = self._insert_recursive(self.root, key, value)
    
    def _insert_recursive(self, node: Optional[TreapNode], key: int, value) -> TreapNode:
        """
        The heart of treap insertion - it's like regular BST insert, but with a twist!
        
        1. Insert like normal BST (following key ordering)
        2. Check if heap property is violated (child has higher priority than parent)
        3. If violated, rotate to fix it
        
        The beauty: rotations happen naturally based on random priorities!
        """
        # Base case: create new node
        if node is None:
            return TreapNode(key, value)
        
        # Standard BST insertion logic
        if key < node.key:
            node.left = self._insert_recursive(node.left, key, value)
            # Heap property check: if left child has higher priority, rotate right
            if node.left.priority > node.priority:
                node = self._rotate_right(node)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, value)
            # Heap property check: if right child has higher priority, rotate left
            if node.right.priority > node.priority:
                node = self._rotate_left(node)
        else:
            # Key already exists, update value
            node.value = value if value is not None else key
        
        return node
    
    def search(self, key: int) -> Optional[TreapNode]:
        """Standard BST search - no rotations needed here!"""
        current = self.root
        while current:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None
    
    def delete(self, key: int) -> None:
        """Delete a key. This is where treaps get a bit tricky."""
        self.root = self._delete_recursive(self.root, key)
    
    def _delete_recursive(self, node: Optional[TreapNode], key: int) -> Optional[TreapNode]:
        """
        Treap deletion strategy:
        1. Find the node to delete
        2. Rotate it down until it becomes a leaf
        3. Remove the leaf
        
        We rotate towards the child with higher priority (maintaining heap property)
        """
        if node is None:
            return None
        
        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Found the node to delete
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Both children exist - rotate towards child with higher priority
                if node.left.priority > node.right.priority:
                    node = self._rotate_right(node)
                    node.right = self._delete_recursive(node.right, key)
                else:
                    node = self._rotate_left(node)
                    node.left = self._delete_recursive(node.left, key)
        
        return node


class SplayNode:
    """
    A node in a Splay Tree.
    
    Splay trees are based on a simple but powerful idea: recently accessed nodes
    should be near the root. This gives excellent performance for non-uniform access patterns.
    
    Think of it like organizing your desk - frequently used items naturally end up on top!
    """
    def __init__(self, key: int, value=None):
        self.key = key
        self.value = value if value is not None else key
        self.left: Optional['SplayNode'] = None
        self.right: Optional['SplayNode'] = None

class SplayTree:
    """
    Splay Tree: The self-adjusting BST that adapts to your access patterns.
    
    Why splay trees are fascinating:
    1. Excellent for non-uniform access (some keys accessed much more than others)
    2. Amortized O(log n) performance - individual operations might be O(n) but average out
    3. Great locality of reference - recently accessed items stay accessible
    4. No need to store balance information (unlike AVL)
    5. Competitive with other balanced trees for many real-world scenarios
    """
    
    def __init__(self):
        self.root: Optional[SplayNode] = None
    
    def _splay(self, node: Optional[SplayNode], key: int) -> Optional[SplayNode]:
        """
        The magic of splay trees - splaying brings a key to the root.
        
        There are three cases (plus their mirrors):
        1. Zig: key is child of root
        2. Zig-Zig: key and parent are both left children (or both right)
        3. Zig-Zag: key is left child of right child (or vice versa)
        
        The key insight: these cases minimize the tree height over many operations!
        """
        if node is None or node.key == key:
            return node
        
        # Key is in left subtree
        if key < node.key:
            if node.left is None:
                return node  # Key not found
            
            # Zig-Zig case (left-left)
            if key < node.left.key:
                # Recursively splay in left-left subtree
                node.left.left = self._splay(node.left.left, key)
                # First rotation
                node = self._rotate_right(node)
            # Zig-Zag case (left-right)
            elif key > node.left.key:
                # Recursively splay in left-right subtree
                node.left.right = self._splay(node.left.right, key)
                # Rotate left child left if needed
                if node.left.right:
                    node.left = self._rotate_left(node.left)
            
            # Second rotation (or first if Zig case)
            return self._rotate_right(node) if node.left else node
        
        # Key is in right subtree (mirror of above)
        else:
            if node.right is None:
                return node  # Key not found
            
            # Zig-Zag case (right-left)
            if key < node.right.key:
                node.right.left = self._splay(node.right.left, key)
                if node.right.left:
                    node.right = self._rotate_right(node.right)
            # Zig-Zig case (right-right)
            elif key > node.right.key:
                node.right.right = self._splay(node.right.right, key)
                node = self._rotate_left(node)
            
            return self._rotate_left(node) if node.right else node
    
    def _rotate_right(self, node: SplayNode) -> SplayNode:
        """Right rotation - same as treap, but used for splaying"""
        left_child = node.left
        node.left = left_child.right
        left_child.right = node
        return left_child
    
    def _rotate_left(self, node: SplayNode) -> SplayNode:
        """Left rotation - same as treap, but used for splaying"""
        right_child = node.right
        node.right = right_child.left
        right_child.left = node
        return right_child
    
    def search(self, key: int) -> Optional[SplayNode]:
        """
        Search and splay - the key insight of splay trees!
        
        Even if we're just searching, we reorganize the tree to make
        this key (and nearby keys) faster to access next time.
        """
        self.root = self._splay(self.root, key)
        return self.root if self.root and self.root.key == key else None
    
    def insert(self, key: int, value=None) -> None:
        """
        Insert with splaying - brings the new key to the root.
        
        Strategy:
        1. Splay the tree around the key
        2. If key exists, update it
        3. If not, split the tree and make key the new root
        """
        if self.root is None:
            self.root = SplayNode(key, value)
            return
        
        self.root = self._splay(self.root, key)
        
        if self.root.key == key:
            # Key already exists, update value
            self.root.value = value if value is not None else key
            return
        
        # Key doesn't exist, create new root
        new_node = SplayNode(key, value)
        if key < self.root.key:
            new_node.right = self.root
            new_node.left = self.root.left
            self.root.left = None
        else:
            new_node.left = self.root
            new_node.right = self.root.right
            self.root.right = None
        
        self.root = new_node
    
    def delete(self, key: int) -> None:
        """
        Delete with splaying - even deletion reorganizes the tree!
        
        Strategy:
        1. Splay the key to the root
        2. If key doesn't exist, we're done
        3. Remove root and splay the maximum key in left subtree
        4. Attach right subtree to the new root
        """
        if self.root is None:
            return
        
        self.root = self._splay(self.root, key)
        
        if self.root.key != key:
            return  # Key not found
        
        if self.root.left is None:
            self.root = self.root.right
        else:
            # Find and splay the maximum in left subtree
            right_subtree = self.root.right
            self.root = self.root.left
            self.root = self._splay_max(self.root)
            self.root.right = right_subtree
    
    def _splay_max(self, node: SplayNode) -> SplayNode:
        """Helper to splay the maximum key in a subtree to the root"""
        while node.right:
            node = self._rotate_left(node)
        return node


class AVLNode:
    """
    A node in an AVL Tree.
    
    AVL trees are the perfectionist's balanced BST - they maintain the strictest
    balance guarantee: heights of left and right subtrees differ by at most 1.
    
    This makes them ideal when you need guaranteed O(log n) performance.
    """
    def __init__(self, key: int, value=None):
        self.key = key
        self.value = value if value is not None else key
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None
        self.height = 1  # Height of this subtree (leaf = 1)

class AVLTree:
    """
    AVL Tree: The original self-balancing BST with guaranteed balance.
    
    Why AVL trees are the gold standard:
    1. Strictest balance guarantee: |height(left) - height(right)| ≤ 1
    2. Guaranteed O(log n) for all operations (no amortization needed)
    3. Excellent for read-heavy workloads
    4. Predictable performance - no surprises
    
    Trade-off: More rotations during insertion/deletion compared to other balanced trees
    """
    
    def __init__(self):
        self.root: Optional[AVLNode] = None
    
    def _get_height(self, node: Optional[AVLNode]) -> int:
        """Get height of a node (0 for None, avoiding null pointer issues)"""
        return node.height if node else 0
    
    def _get_balance(self, node: Optional[AVLNode]) -> int:
        """
        Calculate balance factor: height(left) - height(right)
        
        Balance factor tells us if the tree is left-heavy (+), right-heavy (-), or balanced (0)
        AVL property: balance factor must be in {-1, 0, 1}
        """
        return self._get_height(node.left) - self._get_height(node.right) if node else 0
    
    def _update_height(self, node: AVLNode) -> None:
        """Update height based on children's heights"""
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
    
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        """
        Right rotation for AVL trees.
        
        Used when left subtree is too heavy (balance factor > 1)
        
        Before:     After:
           y           x
          / \         / \
         x   C  -->  A   y
        / \             / \
       A   B           B   C
       
       Heights are recalculated to maintain AVL property
        """
        x = y.left
        y.left = x.right
        x.right = y
        
        # Update heights (order matters - update y first, then x)
        self._update_height(y)
        self._update_height(x)
        
        return x
    
    def _rotate_left(self, x: AVLNode) -> AVLNode:
        """
        Left rotation for AVL trees.
        
        Used when right subtree is too heavy (balance factor < -1)
        """
        y = x.right
        x.right = y.left
        y.left = x
        
        # Update heights (order matters - update x first, then y)
        self._update_height(x)
        self._update_height(y)
        
        return y
    
    def insert(self, key: int, value=None) -> None:
        """Insert a key-value pair maintaining AVL property"""
        self.root = self._insert_recursive(self.root, key, value)
    
    def _insert_recursive(self, node: Optional[AVLNode], key: int, value) -> AVLNode:
        """
        AVL insertion with rebalancing.
        
        The algorithm:
        1. Insert like normal BST
        2. Update height of current node
        3. Check balance factor
        4. If unbalanced, determine rotation type and rotate
        
        Four rotation cases:
        - Left Left: right rotation
        - Right Right: left rotation  
        - Left Right: left rotation on left child, then right rotation
        - Right Left: right rotation on right child, then left rotation
        """
        # Step 1: Standard BST insertion
        if node is None:
            return AVLNode(key, value)
        
        if key < node.key:
            node.left = self._insert_recursive(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, value)
        else:
            # Key already exists, update value
            node.value = value if value is not None else key
            return node
        
        # Step 2: Update height
        self._update_height(node)
        
        # Step 3: Get balance factor
        balance = self._get_balance(node)
        
        # Step 4: If unbalanced, there are 4 cases
        
        # Left Left Case (left subtree is left-heavy)
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        
        # Right Right Case (right subtree is right-heavy)
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        
        # Left Right Case (left subtree is right-heavy)
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Right Left Case (right subtree is left-heavy)
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        # No imbalance, return unchanged node
        return node
    
    def search(self, key: int) -> Optional[AVLNode]:
        """Standard BST search - no rotations needed, just traverse"""
        current = self.root
        while current:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None
    
    def delete(self, key: int) -> None:
        """Delete a key maintaining AVL property"""
        self.root = self._delete_recursive(self.root, key)
    
    def _delete_recursive(self, node: Optional[AVLNode], key: int) -> Optional[AVLNode]:
        """
        AVL deletion with rebalancing.
        
        Similar to insertion but we need to handle the standard BST deletion cases:
        1. Node with no children (leaf)
        2. Node with one child
        3. Node with two children (replace with inorder successor)
        
        Then rebalance like in insertion.
        """
        # Step 1: Standard BST deletion
        if node is None:
            return node
        
        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Node to be deleted found
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Node with two children: get inorder successor
                successor = self._find_min(node.right)
                node.key = successor.key
                node.value = successor.value
                node.right = self._delete_recursive(node.right, successor.key)
        
        # Step 2: Update height
        self._update_height(node)
        
        # Step 3: Get balance factor
        balance = self._get_balance(node)
        
        # Step 4: If unbalanced, there are 4 cases (same as insertion)
        
        # Left Left Case
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)
        
        # Left Right Case
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        
        # Right Right Case
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)
        
        # Right Left Case
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def _find_min(self, node: AVLNode) -> AVLNode:
        """Find the minimum key in a subtree (leftmost node)"""
        while node.left:
            node = node.left
        return node


def demonstrate_trees():
    """
    Let's see these trees in action and understand their different personalities!
    """
    print("🌳 Balanced BST Comparison: Treap vs Splay vs AVL")
    print("=" * 60)
    
    # Create instances of each tree
    treap = Treap()
    splay = SplayTree()
    avl = AVLTree()
    
    # Test data - a mix of sequential and random insertions
    test_keys = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]
    
    print(f"\n📝 Inserting keys: {test_keys}")
    
    # Insert into all trees
    for key in test_keys:
        treap.insert(key)
        splay.insert(key)
        avl.insert(key)
    
    print("\n🔍 Testing search operations:")
    
    # Test searches
    search_keys = [25, 45, 100]  # Mix of existing and non-existing keys
    
    for key in search_keys:
        treap_result = treap.search(key)
        splay_result = splay.search(key)  # This will splay the tree!
        avl_result = avl.search(key)
        
        print(f"Searching for {key}:")
        print(f"  Treap: {'Found' if treap_result else 'Not found'}")
        print(f"  Splay: {'Found' if splay_result else 'Not found'}")
        print(f"  AVL:   {'Found' if avl_result else 'Not found'}")
    
    print("\n🗑️  Testing deletion:")
    
    # Test deletions
    delete_keys = [20, 50]
    
    for key in delete_keys:
        print(f"Deleting {key} from all trees...")
        treap.delete(key)
        splay.delete(key)
        avl.delete(key)
        
        # Verify deletion
        treap_check = treap.search(key)
        splay_check = splay.search(key)
        avl_check = avl.search(key)
        
        if not treap_check and not splay_check and not avl_check:
            print(f"  ✅ {key} successfully deleted from all trees")
        else:
            print(f"  ❌ Deletion failed in some trees")
    
    print("\n🎯 Tree Characteristics Summary:")
    print("""
    🎲 TREAP:
    - Uses randomization for balance (probabilistic)
    - Expected O(log n) operations
    - Simple to implement
    - Good for most general purposes
    
    🎯 SPLAY TREE:
    - Self-adjusting based on access patterns
    - Amortized O(log n) operations
    - Excellent for non-uniform access
    - Recently accessed items stay near root
    
    ⚖️  AVL TREE:
    - Strictly balanced (height difference ≤ 1)
    - Guaranteed O(log n) operations
    - Best for scenarios requiring predictable performance
    - More rotations than other trees
    """)

if __name__ == "__main__":
    demonstrate_trees()
