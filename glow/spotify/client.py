"""Spotify API client — wraps spotipy for current-playback queries."""

from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from unidecode import unidecode

_SCOPES = [
    "user-read-playback-state",
    "user-library-read",
    "user-read-currently-playing",
]

_client: spotipy.Spotify | None = None


def get_client() -> spotipy.Spotify:
    """Return a lazily-initialised Spotify client singleton."""
    global _client
    if _client is None:
        _client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=_SCOPES))
    return _client


def parse_track_info(track: dict[str, Any]) -> dict[str, Any]:
    """Extract relevant fields from a Spotify playback response."""
    album: dict = track["item"]["album"]
    images: list[dict] = album["images"]

    # Pick the smallest thumbnail
    thumb: dict | None = None
    for image in images:
        if thumb is None or image["width"] < thumb["width"]:
            thumb = image

    return {
        "track_name": unidecode(track["item"]["name"]),
        "track_id": track["item"]["id"],
        "track_duration": track["item"]["duration_ms"],
        "track_position": track["progress_ms"],
        "album_name": unidecode(album["name"]),
        "artist_name": unidecode(album["artists"][0]["name"]),
        "thumbnail": thumb["url"] if thumb else None,
    }


def get_current_track_info() -> dict[str, Any] | None:
    """Return parsed info for the currently playing track, or None."""
    current = get_client().current_playback()
    if current and current.get("item"):
        return parse_track_info(current)
    return None


if __name__ == "__main__":
    print(get_current_track_info())
