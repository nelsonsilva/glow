"""Scrolling text visualization for the LED matrix display."""

import argparse
import threading
import time

from PIL import Image, ImageDraw

from glow.display import create_display
from glow.visualizations.utils import load_font

PARAMS: dict = {
    "text": {"type": "text", "name": "Display Text", "default": "Hello World!"},
    "font_size": {
        "type": "select",
        "name": "Font Size",
        "options": ["small", "medium", "large"],
        "default": "large",
    },
    "color": {
        "type": "select",
        "name": "Text Color",
        "options": ["white", "red", "green", "blue", "yellow", "cyan", "magenta"],
        "default": "white",
    },
    "speed": {
        "type": "number",
        "name": "Scroll Speed",
        "min": 1,
        "max": 10,
        "step": 1,
        "default": 3,
    },
}

FONT_MAP = {
    "small": "4x6.pil",
    "medium": "5x7.pil",
    "large": "6x12.pil",
}

COLOR_MAP = {
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
}


def text(
    duration: float = 60.0,
    stop_event: threading.Event | None = None,
    text: str = "Hello World!",
    font_size: str = "large",
    color: str = "white",
    speed: int = 3,
) -> None:
    """Display scrolling text on the LED matrix."""
    display = create_display()
    width, height = display.width, display.height

    font = load_font(FONT_MAP.get(font_size, "6x12.pil"))
    rgb = COLOR_MAP.get(color, (255, 255, 255))

    # Render text onto a wide image
    _, _, text_width, text_height = font.getbbox(text)
    text_img = Image.new("RGB", (text_width + width, height), (0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    y_offset = (height - text_height) // 2
    draw.text((width, y_offset), text, font=font, fill=rgb)

    scroll_x = 0
    total_scroll = text_width + width
    frame_time = 1.0 / 30.0
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline and not (stop_event and stop_event.is_set()):
        frame_start = time.monotonic()

        # Crop the visible portion
        frame = text_img.crop((scroll_x, 0, scroll_x + width, height))
        display.show(frame)

        scroll_x = (scroll_x + speed) % total_scroll

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrolling text visualization")
    parser.add_argument("-d", "--duration", type=float, default=60.0)
    parser.add_argument("-t", "--text", type=str, default="Hello World!")
    parser.add_argument(
        "-f", "--font-size", choices=["small", "medium", "large"], default="large"
    )
    parser.add_argument(
        "-c",
        "--color",
        choices=["white", "red", "green", "blue", "yellow", "cyan", "magenta"],
        default="white",
    )
    parser.add_argument("-s", "--speed", type=int, default=3)
    args = parser.parse_args()
    text(
        duration=args.duration,
        text=args.text,
        font_size=args.font_size,
        color=args.color,
        speed=args.speed,
    )
