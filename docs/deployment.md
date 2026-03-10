# Deployment

## Local Development

```bash
uv sync --extra emulator
DISPLAY_BACKEND=emulator uv run python glow/visualizations/plasma.py
```

The emulator backend opens a window simulating the LED matrix — no hardware needed.

## Pi Deployment

### Install

```bash
uv sync
system/install.sh
```

`install.sh` installs a systemd service (`glow-controller.service`) that:
- Runs as the installing user
- Reads environment variables from `.env`
- Starts the controller via `.venv/bin/glow-controller`
- Restarts on failure (5s delay)
- Waits for network before starting

### Service Management

```bash
sudo systemctl status glow-controller
sudo systemctl restart glow-controller
sudo journalctl -u glow-controller -f
```

## Environment Variables

### MQTT (controller)

| Variable        | Default     |
|-----------------|-------------|
| `MQTT_BROKER`   | `localhost` |
| `MQTT_PORT`     | `1883`      |
| `MQTT_USERNAME` | (none)      |
| `MQTT_PASSWORD` | (none)      |

### Display

See [display spec](/specs/display.md#configuration) for the full `DISPLAY_*` variable table.

### Spotify

Spotify credentials are loaded via dotenv (`.env` file). See `glow/spotify/client.py` for required variables.
