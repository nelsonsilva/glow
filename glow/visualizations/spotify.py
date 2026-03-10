"""Spotify "now playing" visualization for the LED matrix display."""

import argparse
import datetime
import time

from PIL import Image, ImageDraw

from glow.display import create_display
from glow.spotify.client import get_current_track_info
from glow.visualizations.utils import (
    ASSETS_DIR,
    center_text_offset,
    fetch_image,
    load_font,
    resize_icon,
)

from dotenv import load_dotenv
load_dotenv()

SPOTIFY_GREEN = (29, 185, 84)


def _format_time(ms: int) -> str:
    """Format milliseconds as MM:SS."""
    return str(datetime.timedelta(seconds=int(ms / 1000)))[-5:]


def _render_no_track(width: int, height: int) -> Image.Image:
    """Render a placeholder when no track is playing."""
    font = load_font("6x12.pil")
    font5 = load_font("5x7.pil")

    img = Image.new("RGB", (width, height), color=(0, 0, 0))

    icon = Image.open(ASSETS_DIR / "spotify" / "spotify.png").convert("RGB")
    img.paste(icon.resize((64, 64)), (0, 0))

    draw = ImageDraw.Draw(img)

    text = "No Track"
    xoffset = 64 + center_text_offset(text, font, width - 64)
    draw.text((xoffset, 10), text, font=font)

    text = "playing on Spotify"
    xoffset = 64 + center_text_offset(text, font5, width - 64)
    draw.text((xoffset, 30), text, font=font5)

    return img


def _render_track_background(track_info: dict, width: int, height: int) -> Image.Image:
    """Render the static parts of a track display (thumbnail, text, baseline)."""
    font = load_font("6x12.pil")
    font5 = load_font("5x7.pil")
    font4 = load_font("4x6.pil")

    img = Image.new("RGB", (width, height), color=(0, 0, 0))

    # Album thumbnail
    if track_info["thumbnail"]:
        thumb = fetch_image(track_info["thumbnail"])
        resized = resize_icon(thumb, max_height=64)
        img.paste(resized, (0, 0))

    draw = ImageDraw.Draw(img)
    text_area = width - 64

    # Artist name
    xoffset = 64 + center_text_offset(track_info["artist_name"], font, text_area)
    draw.text((xoffset, 2), track_info["artist_name"], font=font)

    # Track name
    xoffset = 64 + center_text_offset(track_info["track_name"], font5, text_area)
    draw.text((xoffset, 20), track_info["track_name"], font=font5)

    # Album name
    xoffset = 64 + center_text_offset(track_info["album_name"], font4, text_area)
    draw.text((xoffset, 40), track_info["album_name"], font=font4)

    # Progress bar baseline
    draw.line((64 + 10, 60, width - 10, 60), fill=(255, 255, 255))

    # Total duration (right side, static)
    end = _format_time(track_info["track_duration"])
    draw.text((width - 20, 52), end, font=font4)

    return img


def spotify(duration: float = 900.0) -> None:
    """Display the currently playing Spotify track on the LED matrix."""
    display = create_display()
    width, height = display.width, display.height

    font4 = load_font("4x6.pil")

    frame = Image.new("RGB", (width, height), color=(0, 0, 0))
    cached_bg: Image.Image | None = None
    cached_track_id: str | None = None
    placeholder: Image.Image | None = None
    track_info: dict | None = None

    poll_interval = 1.0
    last_poll = 0.0
    frame_time = 1.0 / 30.0
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline:
        frame_start = time.monotonic()

        # Poll Spotify API at ~1s intervals
        if time.monotonic() - last_poll >= poll_interval:
            track_info = get_current_track_info()
            last_poll = time.monotonic()

        if track_info is None:
            # Show placeholder
            if placeholder is None:
                placeholder = _render_no_track(width, height)
            display.show(placeholder)
        else:
            # Render/cache background when track changes
            if track_info["track_id"] != cached_track_id or cached_bg is None:
                cached_bg = _render_track_background(track_info, width, height)
                cached_track_id = track_info["track_id"]

            # Composite frame: cached background + dynamic progress
            frame.paste(cached_bg, (0, 0))
            draw = ImageDraw.Draw(frame)

            # Elapsed time (left side)
            elapsed = _format_time(track_info["track_position"])
            draw.text((64 + 2, 52), elapsed, font=font4)

            # Progress bar fill
            bar_start = 64 + 10
            bar_width = width - 10 - bar_start
            progress = int(track_info["track_position"] / track_info["track_duration"] * bar_width)
            draw.line((bar_start, 60, bar_start + progress, 60), fill=SPOTIFY_GREEN)

            display.show(frame)

        # Frame pacing
        elapsed_frame = time.monotonic() - frame_start
        if elapsed_frame < frame_time:
            time.sleep(frame_time - elapsed_frame)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spotify now-playing display")
    parser.add_argument("-d", "--duration", type=float, default=900.0)
    args = parser.parse_args()
    spotify(duration=args.duration)
