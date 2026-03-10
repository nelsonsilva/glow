"""LED Matrix Display Package.

Provides a unified interface for LED matrix displays across different backends:
- Piomatter: Raspberry Pi 5 via adafruit_blinka_raspberry_pi5_piomatter
- Emulator: Local development via RGBMatrixEmulator
- RGBMatrix: Pi Zero 2 WH via rpi-rgb-led-matrix
"""

from .base import Display
from .config import Backend, DisplayConfig, Layout
from .factory import create_display

__all__ = [
    "Backend",
    "Display",
    "DisplayConfig",
    "Layout",
    "create_display",
]
