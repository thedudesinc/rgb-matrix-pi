"""
Depth-First Search (DFS) pathfinding algorithm
Explores as far as possible along each branch before backtracking
Does NOT guarantee shortest path
"""

from .base import PathfindingAlgorithm


class DFSAlgorithm(PathfindingAlgorithm):
    def __init__(self):
        super().__init__("DFS (Depth-First Search)")
    
    def find_path(self, start, end, width, height):
        """
        DFS pathfinding algorithm
        Explores deeply using a stack (implemented recursively)
        """
        stack = [start]
        visited = {start}
        parent = {start: None}
        
        # Explore the grid
        while stack:
            current = stack.pop()
            
            # Yield current state for visualization
            yield ('exploring', current)
            
            # Check if we reached the end
            if current == end:
                # Reconstruct path
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                yield ('found', path)
                return
            
            # Mark as visited after exploring
            yield ('visited', current)
            
            # Explore neighbors (in reverse to maintain consistent direction)
            neighbors = self.get_neighbors(*current, width, height)
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    stack.append(neighbor)
        
        # No path found
        yield ('no_path', None)
