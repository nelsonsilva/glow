import random
import time

import numpy as np
from PIL import Image

from glow.display import create_display

ON = 255
OFF = 0

PALETTES: list[list[tuple[int, int, int]]] = [
    # fire
    [
        (0x03, 0x07, 0x1E),
        (0x37, 0x06, 0x17),
        (0x6A, 0x04, 0x0F),
        (0x9D, 0x02, 0x08),
        (0xD0, 0x00, 0x00),
        (0xDC, 0x2F, 0x02),
        (0xE8, 0x5D, 0x04),
        (0xF4, 0x8C, 0x06),
        (0xFA, 0xA3, 0x07),
        (0xFF, 0xBA, 0x08),
    ],
    # green-blue
    [
        (0xD9, 0xED, 0x92),
        (0xB5, 0xE4, 0x8C),
        (0x99, 0xD9, 0x8C),
        (0x76, 0xC8, 0x93),
        (0x52, 0xB6, 0x9A),
        (0x34, 0xA0, 0xA4),
        (0x16, 0x8A, 0xAD),
        (0x1A, 0x75, 0x9F),
        (0x1E, 0x60, 0x91),
        (0x18, 0x4E, 0x77),
    ],
    # purple-pink
    [
        (0x35, 0x50, 0x70),
        (0x6D, 0x59, 0x7A),
        (0xB5, 0x65, 0x76),
        (0xE5, 0x6B, 0x6F),
        (0xEA, 0xAC, 0x8B),
    ],
    # earth
    [
        (0x58, 0x2F, 0x0E),
        (0x7F, 0x4F, 0x24),
        (0x93, 0x66, 0x39),
        (0xA6, 0x8A, 0x64),
        (0xB6, 0xAD, 0x90),
        (0xC2, 0xC5, 0xAA),
        (0xA4, 0xAC, 0x86),
        (0x65, 0x6D, 0x4A),
        (0x41, 0x48, 0x33),
        (0x33, 0x3D, 0x29),
    ],
    # rainbow
    [
        (0x54, 0x47, 0x8C),
        (0x2C, 0x69, 0x9A),
        (0x04, 0x8B, 0xA8),
        (0x0D, 0xB3, 0x9E),
        (0x16, 0xDB, 0x93),
        (0x83, 0xE3, 0x77),
        (0xB9, 0xE7, 0x69),
        (0xEF, 0xEA, 0x5A),
        (0xF1, 0xC4, 0x53),
        (0xF2, 0x9E, 0x4C),
    ],
    # ice
    [
        (0xCC, 0xDB, 0xDC),
        (0x9A, 0xD1, 0xD4),
        (0x80, 0xCE, 0xD7),
        (0x00, 0x7E, 0xA7),
        (0x00, 0x32, 0x49),
    ],
]


def _random_grid(width: int, height: int) -> np.ndarray:
    """Return a grid with ~20% alive cells."""
    return np.random.choice([ON, OFF], width * height, p=[0.2, 0.8]).reshape(
        width, height
    )


def _run_step(grid: np.ndarray) -> np.ndarray:
    """Advance the simulation one step using toroidal boundary conditions."""
    # Count neighbors using np.roll (toroidal wrapping is automatic)
    neighbors = (
        np.roll(grid, 1, axis=0)
        + np.roll(grid, -1, axis=0)
        + np.roll(grid, 1, axis=1)
        + np.roll(grid, -1, axis=1)
        + np.roll(np.roll(grid, 1, axis=0), 1, axis=1)
        + np.roll(np.roll(grid, 1, axis=0), -1, axis=1)
        + np.roll(np.roll(grid, -1, axis=0), 1, axis=1)
        + np.roll(np.roll(grid, -1, axis=0), -1, axis=1)
    ) // 255

    new_grid = np.zeros_like(grid)
    # Survive: alive cell with 2 or 3 neighbors
    new_grid[(grid == ON) & ((neighbors == 2) | (neighbors == 3))] = ON
    # Birth: dead cell with exactly 3 neighbors
    new_grid[(grid == OFF) & (neighbors == 3)] = ON

    return new_grid


def conway(duration: float = 30.0) -> None:
    """Run Conway's Game of Life with generation trail effect."""
    display = create_display()
    width, height = display.width, display.height

    palette = random.choice(PALETTES)
    tail_length = len(palette)

    grid = _random_grid(width, height)
    generations: list[np.ndarray] = [grid]

    start = time.time()
    while time.time() - start < duration:
        # Build RGB frame as numpy array, then convert to PIL image
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Render each generation in the trail with its palette color
        # Grid is (width, height) so transpose to (height, width) for image coords
        for idx, gen in enumerate(generations):
            mask = gen.T == ON  # (height, width)
            frame[mask] = palette[idx]

        canvas = Image.fromarray(frame)
        display.show(canvas)

        # Advance simulation
        next_gen = _run_step(generations[-1])
        generations.append(next_gen)
        if len(generations) > tail_length:
            generations.pop(0)

        time.sleep(1 / 60.0)


if __name__ == "__main__":
    conway()
