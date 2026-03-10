import math
import time
from PIL import Image
from glow.display import create_display


def plasma(duration: float = 10.0) -> None:
    """Run plasma effect for specified duration."""
    display = create_display()
    width, height = display.width, display.height

    # Pre-compute color palette (256 colors cycling through hues)
    palette = []
    for i in range(256):
        r = int(128 + 127 * math.sin(math.pi * i / 128))
        g = int(128 + 127 * math.sin(math.pi * i / 128 + 2 * math.pi / 3))
        b = int(128 + 127 * math.sin(math.pi * i / 128 + 4 * math.pi / 3))
        palette.append((r, g, b))

    start = time.time()
    while time.time() - start < duration:
        t = time.time() * 2  # Time factor for animation

        canvas = Image.new("RGB", (width, height))
        pixels = canvas.load()

        for y in range(height):
            for x in range(width):
                # Classic plasma formula: sum of multiple sine waves
                v = math.sin(x / 8.0 + t)
                v += math.sin((y + t) / 8.0)
                v += math.sin((x + y + t) / 16.0)
                v += math.sin(math.sqrt(x*x + y*y) / 8.0)

                # Map to palette index (0-255)
                idx = int((v + 4) * 32) % 256
                pixels[x, y] = palette[idx]

        display.show(canvas)
        time.sleep(0.016)  # ~60fps


if __name__ == "__main__":
    plasma()
