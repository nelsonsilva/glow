# Arkanoid

Block breaker game with 4 rows of colored blocks, a bouncing ball, and a paddle.

## Visual Output

Classic Arkanoid layout: 4 rows of colored blocks (red, green, blue, magenta) at the top, a ball that bounces off walls/blocks/paddle, and a paddle near the bottom. Blocks have 3D-style shading. When all blocks are broken, the level resets.

## Modes

- **Auto-play** (default) — paddle tracks the ball automatically. Supports `stop_event` for cooperative cancellation.
- **Interactive** — keyboard input via curses (arrow keys to move, q to quit). Does **not** support `stop_event`.

## Parameters

None.

## Frame Rate

30fps.
