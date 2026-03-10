# Glow - LED Matrix Display Library

A Python library providing a unified interface for LED matrix displays across different hardware backends.

## Supported Backends

| Backend | Hardware | Package |
|---------|----------|---------|
| `piomatter` | Raspberry Pi 5 | `adafruit-blinka-raspberry-pi5-piomatter` |
| `rgbmatrix` | Pi Zero 2 WH | `rpi-rgb-led-matrix` |
| `emulator` | Local development | `RGBMatrixEmulator` |

## Installation

```bash
# Install with uv
uv sync

# For local development (emulator)
uv sync --extra emulator

# For Raspberry Pi 4, Zero, etc..
uv sync --extra pi4

# For Raspberry Pi 5
uv sync --extra pi5
```

## Quick Start

```python
from PIL import Image, ImageDraw
from glow.display import create_display

# Create display (auto-detects backend, or set DISPLAY_BACKEND env var)
display = create_display()

# Draw with PIL
canvas = Image.new("RGB", (display.width, display.height), "black")
draw = ImageDraw.Draw(canvas)
draw.rectangle([10, 5, 50, 25], fill="red")

# Show on display
display.show(canvas)

# Save current state to file
display.capture("/tmp/output.png")
```

## Configuration

Configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DISPLAY_BACKEND` | `auto` | Backend: `piomatter`, `rgbmatrix`, `emulator`, or `auto` |
| `DISPLAY_WIDTH` | `64` | Display width in pixels |
| `DISPLAY_HEIGHT` | `32` | Display height in pixels |
| `DISPLAY_CHAIN_LENGTH` | `1` | Number of chained panels |
| `DISPLAY_PARALLEL` | `1` | Number of parallel chains |
| `DISPLAY_LAYOUT` | `horizontal` | Panel layout: `horizontal` (side-by-side) or `vertical` (stacked) |
| `DISPLAY_HARDWARE_MAPPING` | `adafruit-hat` | Hardware mapping (e.g. `regular`, `adafruit-hat`) |
| `DISPLAY_GPIO_SLOWDOWN` | `1` | GPIO slowdown factor (increase for Pi Zero 2 W) |
| `DISPLAY_DISABLE_HW_PULSING` | `false` | Disable hardware pulsing (`true`/`false`) |

## Running

```bash
# Run with emulator
DISPLAY_BACKEND=emulator uv run python -m glow.main

# Or use the CLI entry point
DISPLAY_BACKEND=emulator uv run glow
```

## Display API

```python
class Display(Protocol):
    width: int              # Display width in pixels
    height: int             # Display height in pixels

    def show(image: Image.Image) -> None
        """Display a PIL Image (RGB mode, sized to width x height)."""

    def clear() -> None
        """Clear display to black."""

    def capture(path: str) -> None
        """Save the current display state to a file."""
```

## Development with Mutagen

Use [Mutagen](https://mutagen.io/) to sync this folder from your Mac to the Pi:

Create a `~/.mutagen.yml` to exclude platform-specific files:

```yaml
sync:
  defaults:
    ignore:
      vcs: true
      paths:
        - ".venv"
```

```bash
mutagen sync create /Users/you/dev/Pi/glow pi-zero:~/glow
```


Each machine maintains its own `.venv` — run `uv sync` on both sides after initial sync.

## Project Structure

```
glow/
├── display/
│   ├── __init__.py      # Package exports
│   ├── base.py          # Display Protocol definition
│   ├── config.py        # Configuration and Backend enum
│   ├── factory.py       # create_display() factory
│   └── backends/
│       ├── emulator.py  # RGBMatrixEmulator backend
│       ├── piomatter.py # Pi 5 backend
│       └── rgbmatrix.py # Pi Zero 2 WH backend
└── main.py              # Example usage
```
