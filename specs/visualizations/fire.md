# Fire

Classic demoscene fire simulation using a heat buffer.

## Algorithm

A 2D heat buffer (width × height+3) of floats 0.0–1.0. Bottom 3 rows are seeded with random values each frame. Heat propagates upward — each cell averages its neighbors below, minus a cooling factor. The cooling factor scales with display height to keep the fire proportional.

## Visual Output

Heat values map to a 256-entry palette with cosine-interpolated transitions: black → deep purple/maroon → bright red → orange → yellow → white.

## Parameters

None.

## Frame Rate

~30fps (33ms sleep).
