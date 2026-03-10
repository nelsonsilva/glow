# Agent Instructions for LED Matrix Visualizations

This document provides instructions for AI agents building visualizations for LED matrix displays.

## Overview

This project provides a display abstraction layer for 64x32 RGB LED matrices. Use the `emulator` backend for development, which runs locally without hardware.

## Build and Run

```bash
# Install dependencies
uv sync --extra emulator

# Run a visualization
DISPLAY_BACKEND=emulator uv run python your_script.py
```

## Creating Visualizations

### Basic Template

```python
from PIL import Image, ImageDraw
from glow.display import create_display

display = create_display()
canvas = Image.new("RGB", (display.width, display.height), "black")
draw = ImageDraw.Draw(canvas)

# Draw your visualization here
draw.rectangle([10, 5, 50, 25], fill="red")

display.show(canvas)
```

### Animation Template

```python
import time
from PIL import Image, ImageDraw
from glow.display import create_display

display = create_display()

for frame in range(100):
    canvas = Image.new("RGB", (display.width, display.height), "black")
    draw = ImageDraw.Draw(canvas)

    # Animate: use 'frame' to change position/color/etc
    x = frame % display.width
    draw.ellipse([x, 10, x + 10, 20], fill="blue")

    display.show(canvas)
    time.sleep(0.016)  # ~60fps
```

## Visual Verification with capture()

The `capture(path)` method saves the current display state to a PNG file. Use this to verify your visualizations are rendering correctly.

### Verification Workflow

1. Write visualization code
2. Call `display.capture('/tmp/output.png')` after `display.show(canvas)`
3. Read the captured image to verify the output
4. Iterate until the visualization is correct

### Static Image Verification

```python
from PIL import Image, ImageDraw
from glow.display import create_display

display = create_display()
canvas = Image.new("RGB", (display.width, display.height), "black")
draw = ImageDraw.Draw(canvas)

# Draw a red rectangle and green circle
draw.rectangle([5, 5, 30, 20], fill="red")
draw.ellipse([40, 5, 60, 25], fill="green")

display.show(canvas)
display.capture("/tmp/verify.png")  # Read this file to verify output
```

### Animation Frame Verification

Capture specific frames during animation to verify motion:

```python
import time
from PIL import Image, ImageDraw
from glow.display import create_display

display = create_display()

for i in range(60):
    canvas = Image.new("RGB", (display.width, display.height), "black")
    draw = ImageDraw.Draw(canvas)

    # Moving circle
    x = i
    draw.ellipse([x, 10, x + 10, 20], fill="blue")
    display.show(canvas)

    # Capture key frames for verification
    if i in [0, 30, 59]:
        display.capture(f"/tmp/frame_{i:03d}.png")

    time.sleep(0.016)
```

### Quick Verification Command

Run inline Python to test and capture:

```bash
DISPLAY_BACKEND=emulator uv run python -c "
from glow.display import create_display
from PIL import Image, ImageDraw

display = create_display()
canvas = Image.new('RGB', (display.width, display.height), 'black')
draw = ImageDraw.Draw(canvas)
draw.rectangle([10, 5, 50, 25], fill=(255, 0, 0))
draw.ellipse([60, 5, 90, 25], fill=(0, 255, 0))

display.show(canvas)
display.capture('/tmp/test.png')
"
```

Then read `/tmp/test.png` to verify the red rectangle and green ellipse rendered correctly.

## Display Specifications

- **Resolution**: 64x32 pixels (default, configurable via `DISPLAY_WIDTH`/`DISPLAY_HEIGHT`)
- **Color**: RGB (24-bit)
- **Coordinate system**: (0,0) is top-left
- **Image format**: PIL `Image.Image` in RGB mode

## PIL Drawing Reference

Common drawing operations for LED matrix visualizations:

```python
from PIL import Image, ImageDraw

canvas = Image.new("RGB", (64, 32), "black")
draw = ImageDraw.Draw(canvas)

# Shapes
draw.rectangle([x1, y1, x2, y2], fill="red", outline="white")
draw.ellipse([x1, y1, x2, y2], fill="blue")
draw.line([x1, y1, x2, y2], fill="green", width=1)
draw.point([x, y], fill="yellow")
draw.polygon([(x1,y1), (x2,y2), (x3,y3)], fill="purple")

# Colors can be:
# - Names: "red", "blue", "green", "black", "white"
# - RGB tuples: (255, 0, 0), (0, 255, 0), (0, 0, 255)
# - Hex: "#FF0000", "#00FF00"

# Text (note: default font is small, good for LED matrix)
draw.text([x, y], "Hi", fill="white")
```

## Tips for LED Matrix Visualizations

1. **Keep it simple**: 64x32 pixels is very limited. Bold shapes and high contrast work best.

2. **Use bright colors**: LED matrices are bright. Pure RGB colors (255,0,0), (0,255,0), (0,0,255) stand out well.

3. **Test with capture()**: Always verify your output looks correct before considering the task complete.

4. **Animation frame rate**: 60fps (~16ms per frame) is smooth. 30fps (~33ms) is acceptable.

5. **Pixel-perfect positioning**: At this resolution, every pixel matters. Use the capture() feedback loop to fine-tune positions.
