# Matrix Rain

Falling columns of characters with brightness trails, inspired by The Matrix.

## Algorithm

Each column tracks a head position, speed, and trail length. Columns fall at randomized speeds. The head character is bright white-green, the trail fades from green to dark green. Random characters from an alphanumeric charset are rendered per cell. When a column passes the bottom plus its trail length, it resets to the top with a new random speed.

## Visual Output

Uses the 4×6 bitmap font — at 4px wide, 48 columns fit across the 192px display. Characters are drawn per-cell with color based on distance from the column head.

## Parameters

None.

## Frame Rate

~25fps (40ms sleep).
