# System Architecture

## Components

```
┌──────────────────┐     MQTT      ┌──────────────────┐
│  Home Assistant  │◄─────────────►│    Controller    │
│  (HA UI)         │               │  (glow.controller)│
└──────────────────┘               └────────┬─────────┘
                                            │
                                            │ starts/stops
                                            ▼
                                   ┌──────────────────┐
                                   │  Visualization   │
                                   │  (daemon thread) │
                                   └────────┬─────────┘
                                            │
                                            │ show(image)
                                            ▼
                                   ┌──────────────────┐
                                   │  Display         │
                                   │  Abstraction     │
                                   └────────┬─────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                         piomatter     rgbmatrix      emulator
                          (Pi 5)      (Pi Zero)       (dev)
```

## How the Pieces Connect

1. **Display abstraction** provides a hardware-agnostic `Display` protocol. Visualizations render PIL images and call `show()`.

2. **Visualizations** are standalone functions that accept `duration`, `stop_event`, and optional params. Each creates its own display instance. They can run independently via CLI or be managed by the controller.

3. **Controller** is an MQTT daemon. It publishes HA discovery payloads on connect, listens for commands (power, viz selection, param changes), and manages a single visualization thread at a time.

4. **Home Assistant** auto-discovers the device via MQTT discovery and provides the UI (select dropdown, power switch, dynamic param controls).
