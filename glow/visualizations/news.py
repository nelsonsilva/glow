"""RSS news ticker visualization for the LED matrix display."""

import argparse
import hashlib
import random
import time
from datetime import datetime

import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode

from glow.display import create_display
from glow.visualizations.utils import (
    ASSETS_DIR,
    FONTS_DIR,
    center_text_offset,
    fetch_image,
    resize_icon,
)

NEWS_DIR = ASSETS_DIR / "news"

FEEDS: list[dict[str, str]] = [
    {
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "name": "nytimes_world",
        "logo": "nyt.png",
    },
    {
        "url": "https://machinelearningmastery.com/blog/feed/",
        "name": "mlm",
        "logo": "mlm.png",
    },
    {
        "url": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml",
        "name": "mit",
        "logo": "MIT-logo.png",
    },
    {
        "url": "https://feeds.feedburner.com/nvidiablog",
        "name": "nvidia",
        "logo": "nvidia.png",
    },
    {
        "url": "https://www.tomshardware.com/feeds/all",
        "name": "tomshardware",
        "logo": "tomshardware.png",
    },
    {
        "url": "https://www.science.org/rss/news_current.xml",
        "name": "science.org",
        "logo": "science.png",
    },
    {
        "url": "https://www.wired.com/feed/rss",
        "name": "wired",
        "logo": "wired.png",
    },
    {
        "url": "https://www.wired.com/feed/category/science/latest/rss",
        "name": "wired science",
        "logo": "wired.png",
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "name": "ars technica",
        "logo": "ars.png",
    },
    {
        "url": "https://www.anandtech.com/rss",
        "name": "anandtech",
        "logo": "anandtech.png",
    },
]


class FeedWrapper:
    """Manages iteration through RSS feed entries with scrolling state."""

    def __init__(self, feed, max_width: int, max_height: int) -> None:
        self.feed = feed
        self.ids = [entry.id for entry in feed.entries]
        self.current_id = self.ids[0]
        self.rendered_img: Image.Image | None = None
        self.rendered_id: str | None = None
        self.max_width = max_width
        self.max_height = max_height
        self.scrolling_position: int | None = None
        self.max_scrolling_position: int = 0

    def get_current_entry(self):
        for entry in self.feed.entries:
            if entry.id == self.current_id:
                return entry
        return None

    def next(self) -> str:
        idx = self.ids.index(self.current_id) + 1
        self.current_id = self.ids[0] if idx >= len(self.ids) else self.ids[idx]
        return self.current_id

    def get_rendered_img(self) -> Image.Image | None:
        if self.rendered_id == self.current_id and self.rendered_img:
            return self.rendered_img
        return None

    def set_rendered_img(self, img: Image.Image, entry_id: str) -> None:
        self.rendered_img = img
        self.rendered_id = entry_id

    def set_scrolling_boundaries(self, text_width: int) -> None:
        self.scrolling_position = self.max_height
        self.max_scrolling_position = -text_width

    def get_next_scrolling_position(self) -> int | None:
        if self.scrolling_position is None:
            return None
        self.scrolling_position -= 1
        if self.scrolling_position < self.max_scrolling_position:
            self.scrolling_position = self.max_width
            return None
        return int(self.scrolling_position)


def _prefetch_thumbnails(feed) -> dict[str, Image.Image]:
    """Download all article thumbnails upfront so the render loop never blocks on I/O."""
    thumbnails: dict[str, Image.Image] = {}
    for entry in feed.entries:
        try:
            thumb_url = entry.media_thumbnail[0]["url"]
            thumbnails[entry.id] = fetch_image(thumb_url)
        except (AttributeError, KeyError, Exception):
            pass
    return thumbnails


def _parse_feed(url: str, max_width: int, max_height: int, max_items: int = 6) -> FeedWrapper:
    """Fetch and parse an RSS feed, extracting thumbnails and cleaning text."""
    feed = feedparser.parse(url)

    if len(feed.entries) > max_items:
        feed.entries = feed.entries[:max_items]

    for entry in feed.entries:
        entry.summary = unidecode(entry.get("summary", ""))
        entry.title = unidecode(entry.title)
        if entry.summary == "":
            entry.summary = entry.title

        if entry.get("id") is None:
            entry.id = hashlib.md5(entry.summary.encode()).hexdigest()

        # Try to find a thumbnail image from various feed formats
        thumb = entry.get("media_thumbnail")
        if thumb is None and "media_content" in entry:
            if "url" in entry.media_content[0]:
                entry["media_thumbnail"] = [{"url": entry.media_content[0]["url"]}]
        if thumb is None and "enc_enclosure" in entry:
            entry["media_thumbnail"] = [{"url": entry.enc_enclosure["rdf:resource"]}]
        elif thumb is None and "content" in entry:
            soup = BeautifulSoup(entry.content[0].value, "html.parser")
            imgs = soup.select("img")
            if imgs:
                entry["media_thumbnail"] = [{"url": imgs[0].get("src")}]
        elif thumb is None and "summary" in entry:
            soup = BeautifulSoup(entry.summary, "html.parser")
            imgs = soup.select("img")
            if imgs:
                entry["media_thumbnail"] = [{"url": imgs[0].get("src")}]
                entry.summary = entry.title

    return FeedWrapper(feed, max_width, max_height)


def news(duration: float = 120.0) -> None:
    """Display scrolling RSS news articles on the LED matrix."""
    display = create_display()
    width, height = display.width, display.height

    font = ImageFont.load(str(FONTS_DIR / "6x12.pil"))
    font5 = ImageFont.load(str(FONTS_DIR / "5x7.pil"))

    # Pick a random feed and fetch it
    feed_def = random.choice(FEEDS)
    print(f"Fetching feed: {feed_def['name']}")
    feed = _parse_feed(feed_def["url"], width, height)

    # Pre-fetch all thumbnails so the render loop never blocks on network I/O
    print("Pre-fetching thumbnails...")
    thumbnails = _prefetch_thumbnails(feed.feed)

    # Pre-load and resize the source logo once
    logo = Image.open(NEWS_DIR / feed_def["logo"]).convert("RGB")
    resized_logo = resize_icon(logo, max_height=30)

    # Reusable frame buffer — avoids allocating a new Image every frame
    frame = Image.new("RGB", (width, height), color=(0, 0, 0))

    # State for text centering
    thumb_size = (0, 0)
    available_text_width = 0

    frame_time = 1.0 / 30.0
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        frame_start = time.monotonic()

        img = feed.get_rendered_img()

        if not img:
            entry = feed.get_current_entry()
            if entry is None:
                feed.next()
                continue

            # Build background image for this article
            img = Image.new("RGB", (width, height), color=(0, 0, 0))

            # Article thumbnail (left side) — use pre-fetched image
            if entry.id in thumbnails:
                resized_thumb = resize_icon(thumbnails[entry.id], max_height=50)
                img.paste(resized_thumb, (0, 0))
                thumb_size = resized_thumb.size
            else:
                thumb_size = (50, 50)

            # Source logo (top-right)
            margin = 1
            img.paste(resized_logo, (width - resized_logo.size[0] - margin, margin))

            draw = ImageDraw.Draw(img)

            # Date text centered between thumbnail and logo
            available_text_width = width - resized_logo.size[0] - thumb_size[0]
            date_text = datetime.now().strftime("%m/%d/%y")
            xoffset = thumb_size[0] + center_text_offset(date_text, font5, available_text_width)
            draw.text((xoffset, 40), date_text, font=font5)

            # Set up horizontal scrolling for summary text
            _, _, text_width, _ = font.getbbox(entry.summary)
            feed.set_scrolling_boundaries(text_width)
            feed.set_rendered_img(img, entry.id)

        # Blit cached background onto reusable frame buffer (avoids img.copy() allocation)
        frame.paste(img, (0, 0))
        entry = feed.get_current_entry()
        if entry is None:
            feed.next()
            continue

        draw = ImageDraw.Draw(frame)

        # Time text (updates every frame)
        time_text = datetime.now().strftime("%H:%M:%S")
        xoffset = thumb_size[0] + center_text_offset(time_text, font, available_text_width)
        draw.text((xoffset, 15), time_text, font=font)

        # Scrolling summary text
        dx = feed.get_next_scrolling_position()
        if dx is None:
            feed.next()
        else:
            draw.text((dx, 50), entry.summary, font=font)

        display.show(frame)

        # Precise frame pacing — account for time spent rendering
        elapsed = time.monotonic() - frame_start
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSS News ticker")
    parser.add_argument("-d", "--duration", type=float, default=120.0)
    args = parser.parse_args()
    news(duration=args.duration)
