"""Display Protocol definition."""

from typing import Protocol

from PIL import Image


class Display(Protocol):
    """Protocol for LED matrix display backends."""

    @property
    def width(self) -> int:
        """Display width in pixels."""
        ...

    @property
    def height(self) -> int:
        """Display height in pixels."""
        ...

    def show(self, image: Image.Image) -> None:
        """Display a PIL Image.

        Image should be RGB mode, sized to width x height.
        """
        ...

    def clear(self) -> None:
        """Clear display to black."""
        ...

    def capture(self, path: str) -> None:
        """Save the current display state to a file."""
        ...
