from PIL import Image
import random

class SnakeGame:
    """Snake game logic and rendering on a logical grid.

    Usage:
      game = SnakeGame(matrix, grid_size=32)
      while running:
          game.step(input_listener)
          image = game.render()
          matrix.SetImage(image)
    """
    def __init__(self, matrix, grid_size=32):
        self.matrix = matrix
        self.grid = grid_size
        self.cell_w = max(1, matrix.width // self.grid)
        self.cell_h = max(1, matrix.height // self.grid)
        self.reset()

    def reset(self):
        self.snake = [(self.grid//2, self.grid//2 + i) for i in range(3)]
        self.direction = (0, -1)
        self.place_food()
        self.alive = True
        self.score = 0

    def place_food(self):
        while True:
            fx = random.randint(0, self.grid-1)
            fy = random.randint(0, self.grid-1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                break

    def step(self, input_listener):
        # update direction from input_listener
        if input_listener.is_pressed('up') and self.direction != (0,1):
            self.direction = (0, -1)
        elif input_listener.is_pressed('down') and self.direction != (0,-1):
            self.direction = (0, 1)
        elif input_listener.is_pressed('left') and self.direction != (1,0):
            self.direction = (-1, 0)
        elif input_listener.is_pressed('right') and self.direction != (-1,0):
            self.direction = (1, 0)

        head = self.snake[0]
        new_head = ((head[0] + self.direction[0]) % self.grid, (head[1] + self.direction[1]) % self.grid)
        if new_head in self.snake:
            self.alive = False
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

    def render(self):
        img = Image.new('RGB', (self.matrix.width, self.matrix.height), (0,0,0))
        for x,y in self.snake:
            for dx in range(self.cell_w):
                for dy in range(self.cell_h):
                    px = x * self.cell_w + dx
                    py = y * self.cell_h + dy
                    if 0 <= px < self.matrix.width and 0 <= py < self.matrix.height:
                        img.putpixel((px, py), (0,255,0))
        # food
        fx, fy = self.food
        for dx in range(self.cell_w):
            for dy in range(self.cell_h):
                px = fx * self.cell_w + dx
                py = fy * self.cell_h + dy
                if 0 <= px < self.matrix.width and 0 <= py < self.matrix.height:
                    img.putpixel((px, py), (255,0,0))
        return img
