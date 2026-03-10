"""Piomatter backend for Raspberry Pi 5."""

import numpy as np
from PIL import Image

from ..config import DisplayConfig


class PiomatterDisplay:
    """Display backend using adafruit_blinka_raspberry_pi5_piomatter for Pi 5."""

    def __init__(self, config: DisplayConfig) -> None:
        from adafruit_blinka_raspberry_pi5_piomatter import (
            Geometry,
            Orientation,
            Pinout,
            PioMatter,
        )

        self._width = config.width
        self._height = config.height

        geometry = Geometry(
            width=config.width,
            height=config.height,
            n_addr_lines=4,
            rotation=Orientation.Normal,
        )

        self._framebuffer = np.zeros(
            (config.height, config.width, 3), dtype=np.uint8
        )

        self._matrix = PioMatter(
            pinout=Pinout.AdafruitMatrixBonnet,
            framebuffer=self._framebuffer,
            geometry=geometry,
        )
        self._last_image: Image.Image | None = None

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def show(self, image: Image.Image) -> None:
        """Display a PIL Image."""
        if image.mode != "RGB":
            image = image.convert("RGB")
        if image.size != (self._width, self._height):
            image = image.resize((self._width, self._height))

        self._last_image = image.copy()
        self._framebuffer[:] = np.array(image)

    def clear(self) -> None:
        """Clear display to black."""
        self._framebuffer[:] = 0

    def capture(self, path: str) -> None:
        """Save the current display state to a file."""
        if self._last_image is not None:
            self._last_image.save(path)
