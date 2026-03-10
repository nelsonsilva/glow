# Threading Model

## Thread Structure

- **Main thread** — runs the MQTT client loop (`loop_start()` + `shutdown.wait()`)
- **Visualization thread** — a single daemon thread running the active visualization

Only one visualization runs at a time. The controller stops the current one before starting a new one.

## Cooperative Cancellation

1. Controller sets `stop_event` (a `threading.Event`)
2. Visualization checks `stop_event.is_set()` in its render loop and exits
3. Controller joins the thread with a 5-second timeout
4. If the thread doesn't stop in time, the controller logs a warning and moves on (thread is a daemon, so it won't block process exit)

## Why Threads, Not Processes

Visualizations share the display hardware — a single process with one active visualization thread avoids resource contention. The GIL is not a bottleneck because the work is I/O-bound (display writes, network calls, sleep).
