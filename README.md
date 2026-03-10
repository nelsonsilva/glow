# Glow - LED Matrix Display Library

A Python library providing a unified interface for LED matrix displays across different hardware backends.

## Supported Backends

| Backend | Hardware | Package |
|---------|----------|---------|
| `piomatter` | Raspberry Pi 5 | `adafruit-blinka-raspberry-pi5-piomatter` |
| `rgbmatrix` | Pi Zero 2 WH | `rpi-rgb-led-matrix` |
| `emulator` | Local development | `RGBMatrixEmulator` |

## Installation

```bash
# Install with uv
uv sync

# For local development (emulator)
uv sync --extra emulator

# For Raspberry Pi 4, Zero, etc..
uv sync --extra pi4

# For Raspberry Pi 5
uv sync --extra pi5
```

## Quick Start

```python
from PIL import Image, ImageDraw
from glow.display import create_display

# Create display (auto-detects backend, or set DISPLAY_BACKEND env var)
display = create_display()

# Draw with PIL
canvas = Image.new("RGB", (display.width, display.height), "black")
draw = ImageDraw.Draw(canvas)
draw.rectangle([10, 5, 50, 25], fill="red")

# Show on display
display.show(canvas)

# Save current state to file
display.capture("/tmp/output.png")
```

## Configuration

Configuration via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DISPLAY_BACKEND` | `auto` | Backend: `piomatter`, `rgbmatrix`, `emulator`, or `auto` |
| `DISPLAY_WIDTH` | `192` | Display width in pixels |
| `DISPLAY_HEIGHT` | `64` | Display height in pixels |
| `DISPLAY_CHAIN_LENGTH` | `1` | Number of chained panels |
| `DISPLAY_PARALLEL` | `3` | Number of parallel chains |
| `DISPLAY_LAYOUT` | `horizontal` | Panel layout: `horizontal` (side-by-side) or `vertical` (stacked) |
| `DISPLAY_HARDWARE_MAPPING` | `regular` | Hardware mapping (e.g. `regular`, `adafruit-hat`) |
| `DISPLAY_GPIO_SLOWDOWN` | `1` | GPIO slowdown factor (increase for Pi Zero 2 W) |
| `DISPLAY_DISABLE_HW_PULSING` | `true` | Disable hardware pulsing (`true`/`false`) |

## Running

```bash
# Run with emulator
DISPLAY_BACKEND=emulator uv run python -m glow.main

# Or use the CLI entry point
DISPLAY_BACKEND=emulator uv run glow
```

## Display API

```python
class Display(Protocol):
    width: int              # Display width in pixels
    height: int             # Display height in pixels

    def show(image: Image.Image) -> None
        """Display a PIL Image (RGB mode, sized to width x height)."""

    def clear() -> None
        """Clear display to black."""

    def capture(path: str) -> None
        """Save the current display state to a file."""
```

## Development with Mutagen

Use [Mutagen](https://mutagen.io/) to sync this folder from your Mac to the Pi:

Create a `~/.mutagen.yml` to exclude platform-specific files:

```yaml
sync:
  defaults:
    ignore:
      vcs: true
      paths:
        - ".venv"
```

```bash
mutagen sync create /Users/you/dev/Pi/glow pi-zero:~/glow
```


Each machine maintains its own `.venv` — run `uv sync` on both sides after initial sync.

## Home Assistant Integration

The Glow controller daemon connects to an MQTT broker and uses [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) so Home Assistant automatically creates a **Glow LED Matrix** device with controls for switching visualizations, toggling power, and adjusting per-visualization parameters.

### Prerequisites

1. **Mosquitto MQTT broker** running on your Home Assistant instance (install via Settings → Add-ons → Mosquitto broker)
2. **MQTT integration** enabled in Home Assistant (Settings → Devices & Services → Add Integration → MQTT)
3. MQTT Discovery enabled (this is on by default)

### Setup

Create an MQTT user for the controller in Home Assistant: Settings → People → Users → Add User. Then configure the connection on the Pi:

```bash
# Add to your .env file (or export as environment variables)
MQTT_BROKER=homeassistant.local   # your HA hostname or IP
MQTT_PORT=1883
MQTT_USERNAME=glow
MQTT_PASSWORD=your_password
```

### Running the controller

```bash
# Using the entry point
uv run glow-controller

# Or as a module
uv run python -m glow.controller

# With explicit arguments (override env vars)
uv run glow-controller --broker 192.168.1.100 --username glow --password secret
```

The controller connects to the broker, publishes discovery configs, and waits for commands. On startup, a **Glow LED Matrix** device appears in Home Assistant under Settings → Devices & Services → MQTT.

### Home Assistant entities

The device exposes these entities:

| Entity | Type | Description |
|--------|------|-------------|
| **Visualization** | Select | Dropdown to pick a visualization (arkanoid, conway, news, plasma, spotify, text) |
| **Power** | Switch | Turn the display on/off (OFF clears the matrix to black) |

When you select a visualization that has configurable parameters (e.g. "text"), additional entities appear dynamically:

| Entity | Type | Description |
|--------|------|-------------|
| **Display Text** | Text | The message to scroll |
| **Font Size** | Select | small / medium / large |
| **Text Color** | Select | white, red, green, blue, yellow, cyan, magenta |
| **Scroll Speed** | Number | 1–10 pixels per frame |

These parameter entities are removed when you switch to a different visualization and replaced with that visualization's own parameters (if any).

### MQTT topics

For debugging or scripting outside of Home Assistant:

| Purpose | Topic | Payload |
|---------|-------|---------|
| Set visualization | `glow/visualization/set` | Visualization name (e.g. `plasma`) |
| Set power | `glow/power/set` | `ON` or `OFF` |
| Set parameter | `glow/param/{name}/set` | Parameter value |
| Visualization state | `glow/visualization/state` | Current visualization name |
| Power state | `glow/power/state` | `ON` or `OFF` |
| Availability | `glow/availability` | `online` or `offline` |

Example with `mosquitto_pub`:

```bash
# Switch to plasma
mosquitto_pub -h homeassistant.local -u glow -P secret -t glow/visualization/set -m plasma

# Switch to text with a custom message
mosquitto_pub -h homeassistant.local -u glow -P secret -t glow/visualization/set -m text
mosquitto_pub -h homeassistant.local -u glow -P secret -t glow/param/text/set -m "Hello from MQTT!"

# Power off
mosquitto_pub -h homeassistant.local -u glow -P secret -t glow/power/set -m OFF
```

### Running as a systemd service

To start the controller automatically on boot:

```bash
sudo tee /etc/systemd/system/glow-controller.service > /dev/null << 'EOF'
[Unit]
Description=Glow LED Matrix Controller
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/glow
EnvironmentFile=/home/pi/glow/.env
ExecStart=/home/pi/glow/.venv/bin/glow-controller
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now glow-controller
```

Check status with `sudo systemctl status glow-controller` and logs with `journalctl -u glow-controller -f`.

### Adding parameters to new visualizations

Any visualization can declare configurable parameters by defining a `PARAMS` dict at the module level. Supported types:

```python
PARAMS = {
    "message": {"type": "text", "name": "Display Name in HA", "default": "hello"},
    "brightness": {"type": "number", "name": "Brightness", "min": 0, "max": 100, "step": 5, "default": 50},
    "mode": {"type": "select", "name": "Mode", "options": ["a", "b", "c"], "default": "a"},
}
```

The visualization function must accept these as keyword arguments alongside `duration` and `stop_event`. The controller passes current values as `**kwargs` when starting the visualization.

## Project Structure

```
glow/
├── controller.py            # MQTT controller daemon (Home Assistant integration)
├── display/
│   ├── __init__.py          # Package exports
│   ├── base.py              # Display Protocol definition
│   ├── config.py            # Configuration and Backend enum
│   ├── factory.py           # create_display() factory
│   └── backends/
│       ├── emulator.py      # RGBMatrixEmulator backend
│       ├── piomatter.py     # Pi 5 backend
│       └── rgbmatrix.py     # Pi Zero 2 WH backend
├── visualizations/
│   ├── __init__.py          # Registry mapping viz names → functions + params
│   ├── arkanoid.py          # Block breaker game
│   ├── conway.py            # Conway's Game of Life
│   ├── news.py              # RSS news ticker
│   ├── plasma.py            # Plasma effect
│   ├── spotify.py           # Spotify now-playing
│   ├── text.py              # Scrolling text (reference viz with PARAMS)
│   └── utils.py             # Shared helpers (fonts, images)
└── main.py                  # Example usage
```
