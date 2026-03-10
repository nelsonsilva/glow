"""Visualization effects for the LED matrix display."""

from glow.visualizations import arkanoid as arkanoid_mod
from glow.visualizations import conway as conway_mod
from glow.visualizations import news as news_mod
from glow.visualizations import plasma as plasma_mod
from glow.visualizations import spotify as spotify_mod
from glow.visualizations import text as text_mod
from glow.visualizations.arkanoid import arkanoid
from glow.visualizations.conway import conway
from glow.visualizations.news import news
from glow.visualizations.plasma import plasma
from glow.visualizations.spotify import spotify
from glow.visualizations.text import text

__all__ = ["arkanoid", "conway", "news", "plasma", "spotify", "text"]

REGISTRY: dict[str, dict] = {
    "arkanoid": {"fn": arkanoid, "params": arkanoid_mod.PARAMS},
    "conway": {"fn": conway, "params": conway_mod.PARAMS},
    "news": {"fn": news, "params": news_mod.PARAMS},
    "plasma": {"fn": plasma, "params": plasma_mod.PARAMS},
    "spotify": {"fn": spotify, "params": spotify_mod.PARAMS},
    "text": {"fn": text, "params": text_mod.PARAMS},
}
