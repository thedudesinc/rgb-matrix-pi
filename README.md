# RGB Matrix Pathfinding Visualizer

A visual demonstration of various pathfinding algorithms on an RGB LED matrix display using a Raspberry Pi.

## Overview

This project visualizes four different pathfinding algorithms in real-time on an LED matrix:

- **BFS (Breadth-First Search)** - Explores nodes level by level, guarantees shortest path
- **DFS (Depth-First Search)** - Explores deeply along branches, does not guarantee shortest path
- **Dijkstra's Algorithm** - Optimal for weighted graphs, guarantees shortest path
- **A\* (A-Star)** - Uses heuristics (Manhattan distance) for efficient pathfinding

Each iteration generates random start and end points, then runs all algorithms sequentially with the same coordinates so you can compare their behavior.

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- RGB LED Matrix (tested with 64x64 matrix)
- RGB Matrix HAT or Bonnet (e.g., Adafruit RGB Matrix HAT)
- 5V power supply for the LED matrix

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/PruessnerN/rgb-matrix-pi.git
   cd rgb-matrix-pi
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install rgbmatrix pillow
   ```

   > Note: The `rgbmatrix` library requires the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library to be installed on your Raspberry Pi.

## Usage

### Basic Usage

Run with default settings (64x64 matrix, 1 iteration):

```bash
sudo python main.py
```

> Note: `sudo` is required for GPIO access on Raspberry Pi.

### Command Line Options

```bash
sudo python main.py [OPTIONS]
```

Available options:

- `--led-rows` - Number of rows in the LED matrix (default: 64)
- `--led-cols` - Number of columns in the LED matrix (default: 64)
- `--led-gpio-mapping` - GPIO mapping type (default: `adafruit-hat`)
  - Options: `adafruit-hat`, `regular`, `adafruit-hat-pwm`, etc.
- `--led-slowdown-gpio` - GPIO slowdown factor (default: 2)
  - Range: 0-4 (0 = no slowdown, higher = more slowdown)
  - Use higher values if you see flickering
- `--iterations` - Number of complete cycles through all algorithms (default: 1)
- `--delay` - Delay between visualization steps in seconds (default: 0.02)

### Examples

Run 3 complete cycles with slower animation:

```bash
sudo python main.py --iterations 3 --delay 0.05
```

Use a 32x32 matrix with regular GPIO mapping:

```bash
sudo python main.py --led-rows 32 --led-cols 32 --led-gpio-mapping regular
```

Reduce flickering with higher GPIO slowdown:

```bash
sudo python main.py --led-slowdown-gpio 4
```

## Color Legend

During visualization, different colors represent different states:

- 🟢 **Green** - Start point
- 🔴 **Red** - End point
- 🔵 **Blue** - Currently exploring node
- ⚫ **Dark Gray** - Visited/processed node
- 🟡 **Yellow** - Final path found

## Project Structure

```
rgb-matrix-pi/
├── main.py                    # Main orchestration script
├── algorithms/                # Pathfinding algorithms
│   ├── __init__.py
│   ├── base.py               # Base class for algorithms
│   ├── bfs.py                # Breadth-First Search
│   ├── dfs.py                # Depth-First Search
│   ├── dijkstra.py           # Dijkstra's Algorithm
│   └── astar.py              # A* Algorithm
├── .gitignore
└── README.md
```

## Adding New Algorithms

To add a new pathfinding algorithm:

1. Create a new file in the `algorithms/` directory (e.g., `bidirectional.py`)
2. Import and inherit from `PathfindingAlgorithm` base class
3. Implement the `find_path(self, start, end, width, height)` method
4. Yield state updates: `('exploring', node)`, `('visited', node)`, `('found', path)`, or `('no_path', None)`
5. Import and add your algorithm to the `algorithms` list in `main.py`

Example:

```python
from algorithms.base import PathfindingAlgorithm

class MyAlgorithm(PathfindingAlgorithm):
    def __init__(self):
        super().__init__("My Custom Algorithm")

    def find_path(self, start, end, width, height):
        # Your implementation here
        yield ('exploring', current_node)
        # ... more logic ...
        yield ('found', path)
```

## Troubleshooting

**Flickering display:**

- Increase `--led-slowdown-gpio` value (try 3 or 4)

**Permission denied:**

- Make sure to run with `sudo`

**Import errors:**

- Ensure you're in the virtual environment: `source .venv/bin/activate`
- Install required libraries: `pip install rgbmatrix pillow`

**Matrix not displaying:**

- Check your hardware connections
- Verify GPIO mapping matches your hardware (`--led-gpio-mapping`)

## License

MIT

## Acknowledgments

- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) by Henner Zeller for the LED matrix library
