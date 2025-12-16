"""
Maze and obstacle generators for pathfinding visualization
"""

import random


def generate_random_walls(width, height, density=0.3, start=None, end=None):
    """
    Generate random wall obstacles
    
    Args:
        width: Grid width
        height: Grid height
        density: Percentage of grid to fill with walls (0.0-1.0)
        start: Starting position to keep clear
        end: Ending position to keep clear
    
    Returns:
        Set of (x, y) coordinates that are walls
    """
    obstacles = set()
    total_cells = width * height
    num_walls = int(total_cells * density)
    
    # Keep areas around start and end clear
    protected = set()
    if start:
        protected.add(start)
        # Keep 3x3 area around start clear
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                px, py = start[0] + dx, start[1] + dy
                if 0 <= px < width and 0 <= py < height:
                    protected.add((px, py))
    
    if end:
        protected.add(end)
        # Keep 3x3 area around end clear
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                px, py = end[0] + dx, end[1] + dy
                if 0 <= px < width and 0 <= py < height:
                    protected.add((px, py))
    
    # Generate random walls
    attempts = 0
    max_attempts = num_walls * 3
    while len(obstacles) < num_walls and attempts < max_attempts:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        if (x, y) not in protected:
            obstacles.add((x, y))
        
        attempts += 1
    
    return obstacles


def generate_maze_walls(width, height, wall_length=5, num_walls=15, start=None, end=None):
    """
    Generate maze-like walls (horizontal and vertical segments)
    
    Args:
        width: Grid width
        height: Grid height
        wall_length: Length of each wall segment
        num_walls: Number of wall segments to create
        start: Starting position to keep clear
        end: Ending position to keep clear
    
    Returns:
        Set of (x, y) coordinates that are walls
    """
    obstacles = set()
    
    # Protected areas around start and end
    protected = set()
    if start:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                px, py = start[0] + dx, start[1] + dy
                if 0 <= px < width and 0 <= py < height:
                    protected.add((px, py))
    
    if end:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                px, py = end[0] + dx, end[1] + dy
                if 0 <= px < width and 0 <= py < height:
                    protected.add((px, py))
    
    for _ in range(num_walls):
        # Random starting point
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        # Random direction (horizontal or vertical)
        if random.random() < 0.5:
            # Horizontal wall
            for i in range(wall_length):
                wx = x + i
                if 0 <= wx < width and (wx, y) not in protected:
                    obstacles.add((wx, y))
        else:
            # Vertical wall
            for i in range(wall_length):
                wy = y + i
                if 0 <= wy < height and (x, wy) not in protected:
                    obstacles.add((x, wy))
    
    return obstacles


def generate_rooms(width, height, num_rooms=4, start=None, end=None):
    """
    Generate rooms with openings (creates interesting pathfinding scenarios)
    
    Args:
        width: Grid width
        height: Grid height
        num_rooms: Number of rectangular rooms to create
        start: Starting position to keep clear
        end: Ending position to keep clear
    
    Returns:
        Set of (x, y) coordinates that are walls
    """
    obstacles = set()
    
    for _ in range(num_rooms):
        # Random room dimensions
        room_width = random.randint(8, 15)
        room_height = random.randint(8, 15)
        
        # Random position
        room_x = random.randint(0, width - room_width)
        room_y = random.randint(0, height - room_height)
        
        # Create room walls
        for x in range(room_x, room_x + room_width):
            obstacles.add((x, room_y))  # Top wall
            obstacles.add((x, room_y + room_height - 1))  # Bottom wall
        
        for y in range(room_y, room_y + room_height):
            obstacles.add((room_x, y))  # Left wall
            obstacles.add((room_x + room_width - 1, y))  # Right wall
        
        # Create 2-3 random openings in the walls
        num_openings = random.randint(2, 3)
        for _ in range(num_openings):
            wall = random.choice(['top', 'bottom', 'left', 'right'])
            
            if wall == 'top':
                opening_x = random.randint(room_x + 1, room_x + room_width - 2)
                obstacles.discard((opening_x, room_y))
            elif wall == 'bottom':
                opening_x = random.randint(room_x + 1, room_x + room_width - 2)
                obstacles.discard((opening_x, room_y + room_height - 1))
            elif wall == 'left':
                opening_y = random.randint(room_y + 1, room_y + room_height - 2)
                obstacles.discard((room_x, opening_y))
            else:  # right
                opening_y = random.randint(room_y + 1, room_y + room_height - 2)
                obstacles.discard((room_x + room_width - 1, opening_y))
    
    # Remove obstacles at start and end
    if start and start in obstacles:
        obstacles.remove(start)
    if end and end in obstacles:
        obstacles.remove(end)
    
    return obstacles
