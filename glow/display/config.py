"""Display configuration."""

import os
from dataclasses import dataclass
from enum import Enum


class Backend(Enum):
    """Supported display backends."""

    PIOMATTER = "piomatter"  # Pi 5
    EMULATOR = "emulator"  # Local dev
    RGBMATRIX = "rgbmatrix"  # Pi Zero 2 WH
    AUTO = "auto"  # Auto-detect


class Layout(Enum):
    """Panel layout when using parallel chains."""

    HORIZONTAL = "horizontal"  # Parallel panels side-by-side (V-mapper)
    VERTICAL = "vertical"  # Parallel panels stacked (default)


@dataclass
class DisplayConfig:
    """Configuration for LED matrix display."""

    width: int = 64 * 3
    height: int = 64
    chain_length: int = 1  # For multiple chained panels
    parallel: int = 3
    backend: Backend = Backend.AUTO
    layout: Layout = Layout.HORIZONTAL
    hardware_mapping: str = "regular"
    gpio_slowdown: int = 1
    disable_hardware_pulsing: bool = True

    @classmethod
    def from_env(cls) -> "DisplayConfig":
        """Load configuration from environment variables.

        Supported environment variables:
        - DISPLAY_BACKEND: piomatter, emulator, rgbmatrix, or auto
        - DISPLAY_WIDTH: Display width in pixels
        - DISPLAY_HEIGHT: Display height in pixels
        - DISPLAY_CHAIN_LENGTH: Number of chained panels
        - DISPLAY_PARALLEL: Number of parallel chains
        - DISPLAY_LAYOUT: horizontal or vertical (panel arrangement)
        - DISPLAY_HARDWARE_MAPPING: Hardware mapping (e.g. regular, adafruit-hat)
        - DISPLAY_GPIO_SLOWDOWN: GPIO slowdown factor
        - DISPLAY_DISABLE_HW_PULSING: Disable hardware pulsing (true/false)
        """
        backend_str = os.environ.get("DISPLAY_BACKEND", "auto").lower()
        try:
            backend = Backend(backend_str)
        except ValueError:
            backend = Backend.AUTO

        layout_str = os.environ.get("DISPLAY_LAYOUT", "horizontal").lower()
        try:
            layout = Layout(layout_str)
        except ValueError:
            layout = Layout.HORIZONTAL

        return cls(
            width=int(os.environ.get("DISPLAY_WIDTH", 64 * 3)),
            height=int(os.environ.get("DISPLAY_HEIGHT", "64")),
            chain_length=int(os.environ.get("DISPLAY_CHAIN_LENGTH", "1")),
            parallel=int(os.environ.get("DISPLAY_PARALLEL", "3")),
            backend=backend,
            layout=layout,
            hardware_mapping=os.environ.get("DISPLAY_HARDWARE_MAPPING", "regular"),
            gpio_slowdown=int(os.environ.get("DISPLAY_GPIO_SLOWDOWN", "1")),
            disable_hardware_pulsing=os.environ.get(
                "DISPLAY_DISABLE_HW_PULSING", "true"
            ).lower()
            in ("true", "1", "yes"),
        )
