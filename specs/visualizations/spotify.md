# Spotify Now Playing

Displays the currently playing Spotify track.

## Visual Output

- **Album art** (64×64, left side)
- **Artist name**, **track name**, **album name** (right side, vertically stacked, centered)
- **Progress bar** with elapsed/total time (bottom)

When nothing is playing, shows a Spotify logo with "No Track" placeholder.

The background (art + text labels) is cached and only re-rendered when the track changes. The progress bar updates every frame.

## Data Source

Polls the Spotify API at ~1-second intervals via `glow.spotify.client.get_current_track_info()`. Requires Spotify API credentials in environment (loaded via dotenv).

## Parameters

None.

## Frame Rate

30fps.
