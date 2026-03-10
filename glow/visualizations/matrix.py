"""Matrix rain (falling characters) visualization for the LED matrix display."""

import argparse
import random
import threading
import time

from PIL import Image, ImageDraw, ImageFont

from glow.display import create_display
from glow.visualizations.utils import FONTS_DIR

PARAMS: dict = {}

# Characters to display — mix of ASCII and simple glyphs
_CHARSET = list("abcdefghijklmnopqrstuvwxyz0123456789!@#$%&*=+<>?/")

# Bright head and trail colors
_HEAD_COLOR = (180, 255, 180)
_BRIGHT_GREEN = (0, 200, 0)


class _Column:
    """A single falling column of characters."""

    __slots__ = ("x", "head_y", "speed", "trail_len", "chars", "height")

    def __init__(self, x: int, height: int) -> None:
        self.x = x
        self.height = height
        self.speed = random.uniform(0.3, 1.0)
        self.trail_len = random.randint(4, height // 2)
        self.head_y = random.uniform(-self.trail_len, 0)
        self.chars: list[str] = [random.choice(_CHARSET) for _ in range(height)]

    def advance(self) -> None:
        self.head_y += self.speed
        # Randomly mutate one character in the trail
        idx = random.randint(0, self.height - 1)
        self.chars[idx] = random.choice(_CHARSET)

    def reset(self) -> None:
        self.head_y = random.uniform(-self.trail_len, -2)
        self.speed = random.uniform(0.3, 1.0)
        self.trail_len = random.randint(4, self.height // 2)


def matrix(duration: float = 30.0, stop_event: threading.Event | None = None) -> None:
    """Run matrix rain effect for specified duration."""
    display = create_display()
    width, height = display.width, display.height

    font = ImageFont.load(str(FONTS_DIR / "4x6.pil"))
    char_w, char_h = 4, 6
    cols = width // char_w
    rows = height // char_h

    # Create columns
    columns = [_Column(c, rows) for c in range(cols)]

    frame_time = 1.0 / 25.0
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline and not (stop_event and stop_event.is_set()):
        frame_start = time.monotonic()

        canvas = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        for col in columns:
            head_row = int(col.head_y)

            for row in range(rows):
                dist = head_row - row
                if dist < 0 or dist >= col.trail_len:
                    continue

                # Color: head is bright white-green, trail fades
                if dist == 0:
                    color = _HEAD_COLOR
                elif dist < col.trail_len // 3:
                    color = _BRIGHT_GREEN
                else:
                    fade = 1.0 - (dist / col.trail_len)
                    g = int(80 * fade)
                    color = (0, max(g, 15), 0)

                char = col.chars[row]
                draw.text((col.x * char_w, row * char_h), char, font=font, fill=color)

            col.advance()
            if head_row > rows + col.trail_len:
                col.reset()

        display.show(canvas)

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matrix rain effect")
    parser.add_argument("-d", "--duration", type=float, default=30.0)
    args = parser.parse_args()
    matrix(duration=args.duration)
