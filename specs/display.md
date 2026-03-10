# Display Abstraction

Unified interface for LED matrix hardware. All visualizations render PIL images and call `display.show(image)` — they never interact with hardware directly.

## Protocol

```
show(image)    — display a PIL RGB Image
clear()        — clear display to black
capture(path)  — save current display state to a PNG file
width          — display width in pixels (read-only)
height         — display height in pixels (read-only)
```

## Backends

| Backend    | Hardware       | Library                                     |
|------------|----------------|---------------------------------------------|
| piomatter  | Raspberry Pi 5 | adafruit-blinka-raspberry-pi5-piomatter     |
| rgbmatrix  | Pi Zero 2 WH   | rpi-rgb-led-matrix                          |
| emulator   | Local dev      | RGBMatrixEmulator                           |

## Auto-Detection Order

When backend is `auto` (default): piomatter → rgbmatrix → emulator. Fails if none are importable.

## Configuration

All configuration via environment variables, loaded by `DisplayConfig.from_env()`.

| Variable                    | Default      | Description                              |
|-----------------------------|--------------|------------------------------------------|
| `DISPLAY_BACKEND`           | `auto`       | Backend selection (piomatter/rgbmatrix/emulator/auto) |
| `DISPLAY_WIDTH`             | `192`        | Display width in pixels                  |
| `DISPLAY_HEIGHT`            | `64`         | Display height in pixels                 |
| `DISPLAY_CHAIN_LENGTH`      | `1`          | Number of chained panels                 |
| `DISPLAY_PARALLEL`          | `3`          | Number of parallel chains                |
| `DISPLAY_LAYOUT`            | `horizontal` | Panel arrangement (horizontal/vertical)  |
| `DISPLAY_HARDWARE_MAPPING`  | `regular`    | Hardware mapping (e.g. regular, adafruit-hat) |
| `DISPLAY_GPIO_SLOWDOWN`     | `1`          | GPIO slowdown factor                     |
| `DISPLAY_DISABLE_HW_PULSING`| `true`      | Disable hardware pulsing (true/false)    |

## Default Dimensions

192×64 — three parallel 64×64 panels in horizontal layout.
