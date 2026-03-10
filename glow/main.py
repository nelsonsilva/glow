"""Example usage of the LED matrix display."""

from PIL import Image, ImageDraw

from glow.display import create_display


def main() -> None:
    """Run example display demo."""
    # Create display (auto-detects backend)
    display = create_display()

    # Draw with PIL
    canvas = Image.new("RGB", (display.width, display.height), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Draw a red rectangle
    draw.rectangle([0, 0, 64, 64], fill=(255, 0, 0))

    # Draw a green ellipse
    draw.ellipse([60, 5, 90, 25], fill=(0, 255, 0))

    # Draw a blue line at the bottom
    y = display.height - 1
    draw.line([0, y, display.width - 1, y], fill=(0, 0, 255), width=2)

    # Show it
    display.show(canvas)
    print(f"Display initialized: {display.width}x{display.height}")
    print("Press Ctrl+C to exit...")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        display.clear()
        print("\nCleared display and exiting.")


if __name__ == "__main__":
    main()
