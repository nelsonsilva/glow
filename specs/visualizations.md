# Visualization System

System-level contract for visualizations. Individual visualization specs live in `specs/visualizations/`.

## Registry

`glow/visualizations/__init__.py` exports a `REGISTRY` dict mapping visualization names to their function and parameter definitions:

```
REGISTRY = {
    "name": {"fn": callable, "params": PARAMS},
    ...
}
```

## Function Contract

Every visualization function accepts:
- `duration: float` — how long to run (seconds)
- `stop_event: threading.Event | None` — cooperative cancellation signal
- Any additional kwargs declared in its `PARAMS` dict

Each visualization creates its own display instance via `create_display()`.

## PARAMS Dict Format

Each visualization module exports a `PARAMS: dict` at module level. Empty dict `{}` means no configurable parameters.

Parameter definition fields:
- `type` — entity type: `"text"`, `"number"`, or `"select"`
- `name` — human-readable label
- `default` — default value

Type-specific fields:
- **number**: `min`, `max`, `step`
- **select**: `options` (list of strings)

## Cooperative Cancellation

Visualizations check `stop_event.is_set()` in their main loop. The controller sets this event when switching visualizations or powering off, then joins the thread with a 5-second timeout.

## Standalone Support

Each visualization supports standalone execution via a `__main__` block with argparse for CLI arguments.
