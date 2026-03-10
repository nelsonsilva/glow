"""RGBMatrixEmulator backend for local development."""

from PIL import Image

from ..config import DisplayConfig


class EmulatorDisplay:
    """Display backend using RGBMatrixEmulator for local development."""

    def __init__(self, config: DisplayConfig) -> None:
        from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

        self._width = config.width
        self._height = config.height
        self._last_image: Image.Image | None = None

        options = RGBMatrixOptions()
        options.rows = config.height
        options.cols = config.width // config.chain_length
        options.chain_length = config.chain_length
        options.parallel = config.parallel

        self._matrix = RGBMatrix(options=options)
        self._canvas = self._matrix.CreateFrameCanvas()

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
        self._canvas.SetImage(image)
        self._canvas = self._matrix.SwapOnVSync(self._canvas)

    def clear(self) -> None:
        """Clear display to black."""
        self._canvas.Clear()
        self._canvas = self._matrix.SwapOnVSync(self._canvas)

    def capture(self, path: str) -> None:
        """Save the current display state to a file."""
        if self._last_image is not None:
            self._last_image.save(path)
