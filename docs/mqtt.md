# MQTT & Home Assistant Integration

## Topics

| Topic                       | Direction | Payload             | Retained |
|-----------------------------|-----------|---------------------|----------|
| `glow/visualization/set`    | command   | visualization name  | —        |
| `glow/visualization/state`  | state     | visualization name  | yes      |
| `glow/power/set`            | command   | ON / OFF            | —        |
| `glow/power/state`          | state     | ON / OFF            | yes      |
| `glow/param/{name}/set`     | command   | parameter value     | —        |
| `glow/param/{name}/state`   | state     | parameter value     | yes      |
| `glow/availability`         | status    | online / offline    | yes      |

## Discovery Payloads

Published to `homeassistant/{type}/{device_id}/{object_id}/config` with retain. Device info is shared across all entities:

```json
{
  "identifiers": ["glow_led_matrix"],
  "name": "Glow LED Matrix",
  "manufacturer": "DIY",
  "model": "RGB LED Matrix"
}
```

Entity types published:
- `select` — visualization picker (options = REGISTRY keys)
- `switch` — power toggle
- `text` / `number` / `select` — per-visualization params (dynamic)

## Dynamic Parameter Entities

When the user selects a visualization:
1. Previous viz's param entities are removed (empty payload published to their config topics)
2. New viz's param entities are published based on its PARAMS dict
3. Current values are published to each param's state topic

## Data Flow

```
HA UI → MQTT broker → controller._on_message()
  → _handle_power() / _handle_visualization() / _handle_param()
    → _start_visualization() → daemon thread → viz function → display.show()
```
