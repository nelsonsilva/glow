# Agent Instructions

## Development Workflow

```bash
uv sync --extra emulator
DISPLAY_BACKEND=emulator uv run python glow/visualizations/your_viz.py
```

**Spec-first**: read the relevant spec in `/specs` before writing code. If the spec needs updating, update it first — specs describe WHAT the system does, not HOW. Update specs when behavior changes.

### Visual Verification

Use `capture()` to verify visualizations render correctly:

1. Write visualization code
2. Call `display.capture('/tmp/output.png')` after `display.show(canvas)`
3. Read the captured image to check the output
4. Iterate until correct

For animations, capture key frames:
```python
if frame_number in [0, 30, 59]:
    display.capture(f"/tmp/frame_{frame_number:03d}.png")
```

## Documentation

- Architecture and technical docs live in `/docs`. Keep them current when making structural changes.
- `README.md` is the user-facing overview. Keep it concise — detailed information belongs in `/docs` and `/specs`. Update the README when adding features, changing setup steps, or modifying the project structure.

## Principles

- **Challenge when needed** — push back on requests that degrade the system
- **Spec-first** — understand and update specs before changing code
- **KISS** — simplest solution that works; no speculative abstractions
- **No hallucinations** — read code before describing it; never guess APIs or behavior
- **DRY** — don't repeat existing utilities; check `glow/visualizations/utils.py` and existing patterns

## Updating This File

Update AGENTS.md when:
- Build/run workflow changes
- New guidelines or conventions are established
- The user requests a persistent behavior change (put it here, not in memory)
