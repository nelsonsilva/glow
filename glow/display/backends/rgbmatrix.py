"""rpi-rgb-led-matrix backend for Pi Zero 2 WH."""

from PIL import Image

from ..config import DisplayConfig, Layout


class RGBMatrixDisplay:
    """Display backend using rpi-rgb-led-matrix for Pi Zero 2 WH."""

    def __init__(self, config: DisplayConfig) -> None:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        self._width = config.width
        self._height = config.height
        self._last_image: Image.Image | None = None

        options = RGBMatrixOptions()
        options.rows = config.height
        options.chain_length = config.chain_length
        options.parallel = config.parallel
        options.hardware_mapping = config.hardware_mapping
        options.gpio_slowdown = config.gpio_slowdown
        options.disable_hardware_pulsing = config.disable_hardware_pulsing

        if config.layout == Layout.HORIZONTAL:
            # V-mapper combines parallel panels side-by-side horizontally
            options.pixel_mapper_config = "V-mapper"
            options.cols = config.width // config.parallel
        else:
            options.cols = config.width // config.chain_length

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
