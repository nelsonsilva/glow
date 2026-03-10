"""Google Calendar agenda visualization for the LED matrix display."""

import argparse
import threading
import time
from datetime import datetime, timezone

from PIL import Image, ImageDraw

from glow.display import create_display
from glow.gcal.client import get_upcoming_events
from glow.visualizations.utils import load_font

from dotenv import load_dotenv

load_dotenv()

PARAMS: dict = {}

# Color palette for calendar event color IDs (Google Calendar uses 1-11)
_EVENT_COLORS = {
    "1": (121, 134, 203),   # Lavender
    "2": (51, 182, 121),    # Sage
    "3": (142, 36, 170),    # Grape
    "4": (251, 140, 0),     # Tangerine
    "5": (246, 191, 38),    # Banana
    "6": (230, 124, 115),   # Flamingo
    "7": (3, 155, 229),     # Peacock
    "8": (97, 97, 97),      # Graphite
    "9": (63, 81, 181),     # Blueberry
    "10": (11, 128, 67),    # Basil
    "11": (213, 0, 0),      # Tomato
}
_DEFAULT_COLOR = (3, 155, 229)  # Peacock blue


def _format_countdown(dt: datetime) -> str:
    """Format time until event as a compact countdown string."""
    now = datetime.now(dt.tzinfo or timezone.utc)
    delta = dt - now

    total_seconds = int(delta.total_seconds())
    if total_seconds <= 0:
        return "NOW"

    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    days = (dt.date() - now.date()).days
    if days >= 1:
        return f"{days}d"
    if hours > 0:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m"


def _format_event_time(dt: datetime) -> str:
    """Format event time as HH:MM, prefixed with day name if not today."""
    now = datetime.now(dt.tzinfo or timezone.utc)
    if dt.date() == now.date():
        return dt.strftime("%H:%M")
    return dt.strftime("%a %H:%M")


def _get_event_color(color_id: str) -> tuple[int, int, int]:
    """Map Google Calendar color ID to RGB."""
    return _EVENT_COLORS.get(color_id, _DEFAULT_COLOR)


def calendar(duration: float = 300.0, stop_event: threading.Event | None = None) -> None:
    """Display upcoming Google Calendar events on the LED matrix."""
    display = create_display()
    width, height = display.width, display.height

    font_large = load_font("6x12.pil")
    font_med = load_font("5x7.pil")
    font_small = load_font("4x6.pil")

    events: list[dict] = []
    last_poll = 0.0
    poll_interval = 60.0
    frame_time = 1.0 / 10.0  # 10fps — calendar is mostly static
    deadline = time.monotonic() + duration

    left_panel_w = 64
    right_panel_x = left_panel_w + 2

    while time.monotonic() < deadline and not (stop_event and stop_event.is_set()):
        frame_start = time.monotonic()

        # Poll calendar API
        if time.monotonic() - last_poll >= poll_interval:
            try:
                events = get_upcoming_events(max_results=4)
            except Exception as e:
                print(f"Calendar fetch error: {e}")
                events = []
            last_poll = time.monotonic()

        canvas = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        if not events:
            draw.text((10, 25), "No upcoming events", font=font_med, fill=(100, 100, 100))
            display.show(canvas)
            elapsed = time.monotonic() - frame_start
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
            continue

        # --- Left panel: countdown to next event ---
        next_event = events[0]
        countdown = _format_countdown(next_event["start"])
        color = _get_event_color(next_event["color"])

        # Draw countdown large and centered in left panel
        draw.text((4, 4), "NEXT", font=font_small, fill=(100, 100, 100))
        _, _, cw, _ = font_large.getbbox(countdown)
        cx = max(0, (left_panel_w - cw) // 2)
        draw.text((cx, 18), countdown, font=font_large, fill=color)

        # Truncate title to fit left panel
        title_short = next_event["title"][:10]
        draw.text((2, 35), title_short, font=font_small, fill=(180, 180, 180))

        # Time of next event
        time_str = _format_event_time(next_event["start"])
        draw.text((2, 45), time_str, font=font_med, fill=(150, 150, 150))

        # Separator line
        draw.line((left_panel_w, 0, left_panel_w, height), fill=(40, 40, 40))

        # --- Right panel: agenda (two lines per event) ---
        y = 2
        max_title_chars = (width - right_panel_x - 6) // 4
        for event in events:
            if y + 12 > height:
                break

            evt_color = _get_event_color(event["color"])
            time_text = _format_event_time(event["start"])
            title = event["title"]

            # Line 1: color dot + time
            draw.rectangle(
                (right_panel_x, y + 1, right_panel_x + 3, y + 4),
                fill=evt_color,
            )
            draw.text((right_panel_x + 6, y), time_text, font=font_small, fill=(120, 120, 120))

            # Line 2: title (indented, truncated to fit)
            if len(title) > max_title_chars:
                title = title[: max_title_chars - 1] + "."
            draw.text((right_panel_x + 6, y + 7), title, font=font_small, fill=(200, 200, 200))

            y += 16

        display.show(canvas)

        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Calendar agenda display")
    parser.add_argument("-d", "--duration", type=float, default=300.0)
    args = parser.parse_args()
    calendar(duration=args.duration)
