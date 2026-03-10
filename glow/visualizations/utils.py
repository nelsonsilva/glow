"""Shared helpers for visualizations."""

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from PIL import Image, ImageFont

ASSETS_DIR = Path(__file__).parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"


def resize_icon(
    icon: Image.Image,
    max_height: int | None = None,
    max_width: int | None = None,
) -> Image.Image:
    """Resize icon to fit max_height or max_width, preserving aspect ratio."""
    icon_width, icon_height = icon.size
    if max_height:
        icon_width = int(icon_width / (icon_height / max_height))
        icon_height = max_height
    elif max_width:
        icon_height = int(icon_height / (icon_width / max_width))
        icon_width = max_width
    return icon.resize((icon_width, icon_height), Image.Resampling.LANCZOS)


def center_text_offset(text: str, font: ImageFont.ImageFont, available_width: int) -> int:
    """Compute x-offset to center text within available_width."""
    _, _, text_width, _ = font.getbbox(text)
    if text_width < available_width:
        return int((available_width - text_width) / 2)
    return 0


def fetch_image(url: str) -> Image.Image:
    """Download an image from a URL and return as RGB PIL Image."""
    return Image.open(BytesIO(urlopen(url).read())).convert("RGB")


def load_font(name: str) -> ImageFont.ImageFont:
    """Load a bitmap font from the assets/fonts directory."""
    return ImageFont.load(str(FONTS_DIR / name))
