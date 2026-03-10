"""Arkanoid (block breaker) visualization with optional interactive play."""

import random
import curses
import threading
import time

from PIL import Image, ImageDraw

from glow.display import create_display

PARAMS: dict = {}

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
FRICTION: float = 0.9
SPEED_IMPULSION: float = 1.0


def darker(color: tuple, pct: int) -> tuple:
    return tuple(int(c * pct / 100) for c in color)


def lighter(color: tuple, pct: int) -> tuple:
    return tuple(
        int((pct / 100) * 255) if c == 0 else min(int(c * (1 + pct / 100)), 255)
        for c in color
    )


class Ball:
    def __init__(self, x: int, y: int, color: tuple, r: int) -> None:
        self.color = color
        self.x: float = x
        self.y: float = y
        self.r: int = r
        vx: float = random.randint(-10, 10)
        if vx == 0:
            vx += 1
        vx = 1.0 / vx
        self.speed: tuple[float, float] = (vx, -1.7)

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        draw.ellipse(
            (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r),
            fill=self.color,
            outline=darker(self.color, 70),
        )

    def move(self) -> None:
        self.x += self.speed[0]
        self.y += self.speed[1]


class Paddle:
    def __init__(self, x: int, y: int, width: int) -> None:
        self.x = x
        self.y = y
        self.width: int = width
        self.x_speed: float = 0

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        color = (200, 200, 200)
        hw = self.width / 2
        draw.rectangle(
            (self.x - hw, self.y, self.x + hw, self.y + 4),
            fill=color,
            outline=darker(color, 50),
        )
        red = (255, 0, 0)
        draw.rectangle(
            (self.x - hw + 1, self.y - 1, self.x - hw + 5, self.y + 5),
            fill=red,
            outline=darker(red, 50),
        )
        draw.rectangle(
            (self.x + hw - 5, self.y - 1, self.x + hw - 1, self.y + 5),
            fill=red,
            outline=darker(red, 50),
        )
        self.x += self.x_speed
        self.x_speed = FRICTION * self.x_speed

    def bounce(self, ball: Ball) -> bool:
        if ball.speed[1] > 0 and self.x - self.width / 2 < ball.x < self.x + self.width / 2:
            if abs(self.y - ball.y) <= ball.r:
                ball.speed = (ball.speed[0], -ball.speed[1])
                return True
        return False

    def input(self, direction: str) -> None:
        if direction == "LEFT":
            self.x_speed -= SPEED_IMPULSION
        elif direction == "RIGHT":
            self.x_speed += SPEED_IMPULSION

    def auto_play(self, ball: Ball) -> None:
        """Move paddle toward ball's x position."""
        if ball.x < self.x - 2:
            self.x_speed -= SPEED_IMPULSION
        elif ball.x > self.x + 2:
            self.x_speed += SPEED_IMPULSION


class Block:
    def __init__(self, color: tuple, xy: tuple) -> None:
        self.color = color
        self.xy = xy
        self.broken: bool = False

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        if self.broken:
            return
        draw.rectangle(self.xy, fill=self.color, outline=darker(self.color, 70))
        draw.line(
            (self.xy[0], self.xy[1], self.xy[2], self.xy[1]),
            fill=lighter(self.color, 30),
        )
        draw.line(
            (self.xy[2], self.xy[1], self.xy[2], self.xy[3]),
            fill=lighter(self.color, 30),
        )

    def bounce(self, ball: Ball) -> bool:
        # Bounce from below
        if (
            ball.speed[1] < 0
            and self.xy[0] <= ball.x <= self.xy[2]
            and abs(self.xy[3] - ball.y) < ball.r
        ):
            ball.speed = (ball.speed[0], -ball.speed[1])
            self.broken = True

        # Bounce from top
        if (
            ball.speed[1] > 0
            and self.xy[0] <= ball.x <= self.xy[2]
            and abs(self.xy[1] - ball.y) < ball.r
        ):
            ball.speed = (ball.speed[0], -ball.speed[1])
            self.broken = True

        # Bounce from left
        if (
            ball.speed[0] < 0
            and self.xy[1] <= ball.y <= self.xy[3]
            and abs(self.xy[2] - ball.x) < ball.r
        ):
            ball.speed = (-ball.speed[0], ball.speed[1])
            self.broken = True

        # Bounce from right
        if (
            ball.speed[0] > 0
            and self.xy[1] <= ball.y <= self.xy[3]
            and abs(self.xy[0] - ball.x) < ball.r
        ):
            ball.speed = (-ball.speed[0], ball.speed[1])
            self.broken = True

        return self.broken


class Zone:
    def __init__(self, x: int, y: int, size: int) -> None:
        self.x: int = x
        self.y: int = y
        self.size: int = size
        self.actors: list[Block] = []

    def add_actor(self, actor: Block) -> None:
        self.actors.append(actor)

    def inside(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.size and self.y <= y < self.y + self.size

    def inside_r(self, x: int, y: int, r: int) -> bool:
        return (
            self.inside(x + r, y + r)
            or self.inside(x - r, y + r)
            or self.inside(x + r, y - r)
            or self.inside(x - r, y - r)
        )

    def inside_xy(self, xy: tuple) -> bool:
        return self.inside(xy[0], xy[1]) or self.inside(xy[2], xy[3])


class Grid:
    def __init__(self, width: int, height: int, size: int) -> None:
        self.zones: list[Zone] = []
        for x in range(int(width / size) + 1):
            for y in range(int(height / size) + 1):
                self.zones.append(Zone(x * size, y * size, size))

    def add_block(self, block: Block) -> None:
        for zone in self.zones:
            if zone.inside_xy(block.xy):
                zone.add_actor(block)

    def find_blocks(self, x: int, y: int, r: int) -> list[Block]:
        blocks: list[Block] = []
        for zone in self.zones:
            if zone.inside_r(x, y, r):
                blocks.extend(zone.actors)
        return blocks


class Stage:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.blocks: list[Block] = []
        self.grid: Grid = Grid(width, height, 16)
        self.setup_level()
        self.ball = Ball(int(width / 2), int(height * 0.85), (240, 240, 200), 2)
        self.paddle = Paddle(int(width / 2), int(height * 0.90), 26)

    def setup_level(self) -> None:
        self.blocks.clear()
        self.grid = Grid(self.width, self.height, 16)

        b_width = 16
        b_height = 4
        b_margin = 2

        x_steps = int(self.width / (b_width + b_margin))
        decal_x = (self.width - (x_steps * (b_width + b_margin))) // 2

        for y in range(4):
            color = COLORS[y]
            for x in range(x_steps):
                x0 = decal_x + x * (b_width + b_margin)
                y0 = b_margin + y * (b_height + b_margin)
                x1 = x0 + b_width
                y1 = y0 + b_height
                block = Block(color, (x0, y0, x1, y1))
                self.blocks.append(block)
                self.grid.add_block(block)

    def draw(self, draw: ImageDraw.ImageDraw) -> None:
        for block in self.blocks:
            block.draw(draw)
        self.ball.draw(draw)
        self.paddle.draw(draw)

    def reset(self) -> None:
        self.ball = Ball(
            int(self.width / 2), int(self.height * 0.85), (240, 240, 200), 2
        )

    def play(self) -> None:
        self.ball.move()

        # Wall bounces
        if self.ball.y < self.ball.r:
            self.ball.speed = (self.ball.speed[0], -self.ball.speed[1])
        elif self.ball.y > self.height - self.ball.r:
            self.reset()
        if self.ball.x < self.ball.r:
            self.ball.speed = (-self.ball.speed[0], self.ball.speed[1])
        elif self.ball.x > self.width - self.ball.r:
            self.ball.speed = (-self.ball.speed[0], self.ball.speed[1])

        # Block collisions
        blocks = self.grid.find_blocks(
            int(self.ball.x), int(self.ball.y), int(self.ball.r)
        )
        for block in blocks:
            if not block.broken and block.bounce(self.ball):
                break

        # Paddle bounce
        self.paddle.bounce(self.ball)

        # Level reset when all blocks broken
        if all(block.broken for block in self.blocks):
            self.setup_level()


def _run_auto(duration: float, stop_event: threading.Event | None = None) -> None:
    """Run Arkanoid in auto-play mode."""
    display = create_display()
    stage = Stage(display.width, display.height)
    frame_time = 1.0 / 30.0

    end_time = time.monotonic() + duration
    while time.monotonic() < end_time and not (stop_event and stop_event.is_set()):
        frame_start = time.monotonic()

        canvas = Image.new("RGB", (display.width, display.height), (0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        stage.paddle.auto_play(stage.ball)
        stage.draw(draw)
        stage.play()

        display.show(canvas)

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


def _run_interactive(stdscr: curses.window, duration: float) -> None:
    """Run Arkanoid with keyboard input via curses."""
    stdscr.nodelay(True)
    stdscr.timeout(0)
    curses.curs_set(0)

    display = create_display()
    stage = Stage(display.width, display.height)
    frame_time = 1.0 / 30.0

    end_time = time.monotonic() + duration
    while time.monotonic() < end_time:
        frame_start = time.monotonic()

        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            stage.paddle.input("LEFT")
        elif key == curses.KEY_RIGHT:
            stage.paddle.input("RIGHT")
        elif key == ord("q"):
            break

        canvas = Image.new("RGB", (display.width, display.height), (0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        stage.draw(draw)
        stage.play()

        display.show(canvas)

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


def arkanoid(
    duration: float = 60.0,
    interactive: bool = False,
    stop_event: threading.Event | None = None,
) -> None:
    """Arkanoid (block breaker) visualization.

    Args:
        duration: How long to run in seconds.
        interactive: If True, use keyboard input (arrow keys) instead of auto-play.
        stop_event: Optional threading event for cooperative cancellation.
    """
    if interactive:
        curses.wrapper(_run_interactive, duration)
    else:
        _run_auto(duration, stop_event)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Arkanoid visualization")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Play interactively with arrow keys (q to quit)")
    parser.add_argument("-d", "--duration", type=float, default=60.0,
                        help="Duration in seconds (default: 60)")
    args = parser.parse_args()
    arkanoid(duration=args.duration, interactive=args.interactive)
