# MQTT Controller

Daemon that bridges Home Assistant and visualizations via MQTT.

## Purpose

Listens for MQTT commands to select visualizations, toggle power, and adjust parameters. Publishes MQTT Discovery payloads so Home Assistant auto-discovers the device without manual configuration.

## MQTT Discovery

On connect, publishes discovery configs for:
- **Select entity** — visualization picker (options from REGISTRY keys)
- **Switch entity** — power on/off

When a visualization is selected, publishes dynamic parameter entities based on that visualization's PARAMS dict. Previous visualization's param entities are removed (empty payload with retain).

## Entities

| Entity | Type   | Purpose                        |
|--------|--------|--------------------------------|
| Visualization | select | Pick active visualization |
| Power  | switch | Turn display on/off            |
| Params | text/number/select | Per-visualization settings (dynamic) |

## Topics

| Topic                       | Direction | Purpose                     |
|-----------------------------|-----------|-----------------------------|
| `glow/visualization/set`    | command   | Set active visualization    |
| `glow/visualization/state`  | state     | Current visualization name  |
| `glow/power/set`            | command   | ON/OFF                      |
| `glow/power/state`          | state     | Current power state         |
| `glow/param/{name}/set`     | command   | Set parameter value         |
| `glow/param/{name}/state`   | state     | Current parameter value     |
| `glow/availability`         | state     | online/offline              |

## Lifecycle

1. **Power ON** — if a visualization is selected, starts it in a daemon thread
2. **Power OFF** — stops current visualization, clears display to black
3. **Viz switch** — stops current visualization, initializes default params, publishes param entities, starts new visualization (if powered on)
4. **Param change** — updates stored value, restarts visualization with new params (if powered on)

## Configuration

CLI args with environment variable fallbacks:

| Arg          | Env Variable    | Default     |
|--------------|-----------------|-------------|
| `--broker`   | `MQTT_BROKER`   | `localhost` |
| `--port`     | `MQTT_PORT`     | `1883`      |
| `--username` | `MQTT_USERNAME` | (none)      |
| `--password` | `MQTT_PASSWORD` | (none)      |

## Deployment

Systemd service installed via `system/install.sh`. The service unit reads environment from `.env`, runs as the installing user, and restarts on failure.
