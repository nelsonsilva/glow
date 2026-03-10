"""Display factory for creating display backends."""

from .base import Display
from .config import Backend, DisplayConfig


def _detect_backend() -> Backend:
    """Auto-detect the best available backend."""
    # Try piomatter first (Pi 5)
    try:
        import adafruit_blinka_raspberry_pi5_piomatter  # noqa: F401

        return Backend.PIOMATTER
    except ImportError:
        pass

    # Try rgbmatrix (Pi Zero 2 WH)
    try:
        import rgbmatrix  # noqa: F401

        return Backend.RGBMATRIX
    except ImportError:
        pass

    # Try emulator (local dev)
    try:
        import RGBMatrixEmulator  # noqa: F401

        return Backend.EMULATOR
    except ImportError:
        pass

    raise RuntimeError(
        "No display backend available. Install one of: "
        "adafruit-blinka-raspberry-pi5-piomatter, "
        "rpi-rgb-led-matrix, or RGBMatrixEmulator"
    )


def create_display(config: DisplayConfig | None = None) -> Display:
    """Create a display instance based on configuration.

    Args:
        config: Display configuration. If None, loads from environment variables.

    Returns:
        A Display instance for the configured backend.

    Raises:
        RuntimeError: If no backend is available or the specified backend
            cannot be imported.
    """
    if config is None:
        config = DisplayConfig.from_env()

    backend = config.backend
    if backend == Backend.AUTO:
        backend = _detect_backend()

    if backend == Backend.PIOMATTER:
        from .backends.piomatter import PiomatterDisplay

        return PiomatterDisplay(config)

    if backend == Backend.EMULATOR:
        from .backends.emulator import EmulatorDisplay

        return EmulatorDisplay(config)

    if backend == Backend.RGBMATRIX:
        from .backends.rgbmatrix import RGBMatrixDisplay

        return RGBMatrixDisplay(config)

    raise RuntimeError(f"Unknown backend: {backend}")
