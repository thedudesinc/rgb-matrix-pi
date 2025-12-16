"""
Breadth-First Search (BFS) pathfinding algorithm
Explores nodes level by level, guarantees shortest path
"""

from collections import deque
from .base import PathfindingAlgorithm


class BFSAlgorithm(PathfindingAlgorithm):
    def __init__(self):
        super().__init__("BFS (Breadth-First Search)")
    
    def find_path(self, start, end, width, height):
        """
        BFS pathfinding algorithm
        Explores nodes level by level using a queue
        """
        queue = deque([start])
        visited = {start}
        parent = {start: None}
        
        # Explore the grid
        while queue:
            current = queue.popleft()
            
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
            
            # Explore neighbors
            for neighbor in self.get_neighbors(*current, width, height):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        # No path found
        yield ('no_path', None)
