"""Classic demoscene fire effect for the LED matrix display."""

import argparse
import math
import threading
import time

import numpy as np
from PIL import Image
from glow.display import create_display

PARAMS: dict = {}

# Pre-compute fire palette with cosine interpolation through control points
_CONTROL_POINTS = [
    (0, (0, 0, 0)),          # black
    (50, (40, 0, 30)),       # deep purple/maroon
    (100, (200, 10, 0)),     # bright red
    (160, (255, 140, 0)),    # orange
    (210, (255, 230, 50)),   # yellow
    (240, (255, 255, 200)),  # bright yellow-white
    (255, (255, 255, 255)),  # white
]

_PALETTE = np.zeros((256, 3), dtype=np.uint8)
for _seg in range(len(_CONTROL_POINTS) - 1):
    _i0, _c0 = _CONTROL_POINTS[_seg]
    _i1, _c1 = _CONTROL_POINTS[_seg + 1]
    for _i in range(_i0, _i1 + 1):
        _t = (_i - _i0) / (_i1 - _i0) if _i1 != _i0 else 1.0
        # Cosine interpolation for smooth blending
        _t = (1.0 - math.cos(_t * math.pi)) / 2.0
        _PALETTE[_i] = tuple(int(_c0[c] + (_c1[c] - _c0[c]) * _t) for c in range(3))


def fire(duration: float = 30.0, stop_event: threading.Event | None = None) -> None:
    """Run fire effect for specified duration."""
    display = create_display()
    width, height = display.width, display.height

    # Heat buffer — extra rows at the bottom for seeding
    heat = np.zeros((height + 3, width), dtype=np.float64)

    cooling = 1.0 / height  # Cooling factor scales with height
    blend = 0.4  # How much of the new propagation to mix in per frame
    frame_time = 1.0 / 30.0
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline and not (stop_event and stop_event.is_set()):
        frame_start = time.monotonic()

        # Seed bottom 3 rows with random heat
        heat[-3:, :] = np.random.random((3, width)) * 0.8 + 0.2

        # Propagate heat upward: average of neighbors below, minus cooling
        # Blend with previous frame for slower, smoother movement
        for y in range(height - 1, -1, -1):
            left = np.roll(heat[y + 1], 1)
            right = np.roll(heat[y + 1], -1)
            avg = (heat[y + 1] + heat[y + 2] + left + right) / 4.0
            new = avg - cooling - np.random.random(width) * cooling
            heat[y] = np.clip(heat[y] * (1.0 - blend) + new * blend, 0.0, 1.0)

        # Map heat values to palette indices and build image
        indices = (heat[:height] * 255).astype(np.uint8)
        rgb = _PALETTE[indices]  # shape: (height, width, 3)
        canvas = Image.fromarray(rgb, "RGB")

        display.show(canvas)

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fire effect")
    parser.add_argument("-d", "--duration", type=float, default=30.0)
    args = parser.parse_args()
    fire(duration=args.duration)
