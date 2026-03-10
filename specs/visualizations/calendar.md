# Google Calendar

Displays upcoming events from Google Calendar.

## API Client

Uses `google-api-python-client` + `google-auth-oauthlib` for OAuth2. First run opens a browser for consent and saves the token to `.gcal_token.json`. Polls every 60 seconds.

## Layout (192×64)

- **Left panel** (~64px): Large countdown to next event ("23m", "1h15m", or "NOW"), event title snippet, and start time.
- **Right panel** (~128px): Scrolling agenda of next 5 events with color dot, time, and title.

## Color Coding

Events are color-coded using Google Calendar's 11-color palette, mapped to RGB values.

## Parameters

None.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CALENDAR_ID` | `primary` | Calendar to fetch events from |

## Credentials

Requires a `credentials.json` file (Google OAuth2 client credentials) in the project root. On first run, opens a browser for authorization and saves the token to `.gcal_token.json`.

## Frame Rate

~10fps (100ms sleep). Calendar data is slow-moving so high frame rates are unnecessary.
