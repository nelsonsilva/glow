# Scrolling Text

Horizontally scrolling text message.

## Visual Output

Text renders onto a wide offscreen image, then a viewport-sized crop scrolls left each frame. Text is vertically centered. Wraps continuously — when the text scrolls fully off-screen, it reappears from the right.

## Parameters

| Name      | Type   | Default        | Details                                              |
|-----------|--------|----------------|------------------------------------------------------|
| text      | text   | "Hello World!" | The message to display                               |
| font_size | select | large          | Options: small (4x6), medium (5x7), large (6x12)    |
| color     | select | white          | Options: white, red, green, blue, yellow, cyan, magenta |
| speed     | number | 3              | Pixels per frame (1–10)                              |

## Frame Rate

30fps.
