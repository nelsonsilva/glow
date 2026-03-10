"""Google Calendar API client — fetches upcoming events via OAuth2."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
_TOKEN_PATH = Path(__file__).parent.parent.parent / ".gcal_token.json"
_CREDENTIALS_PATH = Path(__file__).parent.parent.parent / "credentials.json"

_service = None


def _get_service():
    """Return a lazily-initialised Calendar API service singleton."""
    global _service
    if _service is not None:
        return _service

    creds = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDENTIALS_PATH), _SCOPES)
            creds = flow.run_local_server(port=0)
        _TOKEN_PATH.write_text(creds.to_json())

    _service = build("calendar", "v3", credentials=creds)
    return _service


def get_upcoming_events(max_results: int = 5) -> list[dict[str, Any]]:
    """Fetch the next upcoming events from Google Calendar.

    Returns a list of dicts with keys: title, start, end, calendar, color.
    """
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    service = _get_service()

    now = datetime.now(timezone.utc).isoformat()
    result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []
    for item in result.get("items", []):
        start_raw = item["start"].get("dateTime", item["start"].get("date"))
        end_raw = item["end"].get("dateTime", item["end"].get("date"))

        # Parse datetime — handle both date and dateTime formats
        try:
            start = datetime.fromisoformat(start_raw)
        except ValueError:
            start = datetime.strptime(start_raw, "%Y-%m-%d")

        try:
            end = datetime.fromisoformat(end_raw)
        except ValueError:
            end = datetime.strptime(end_raw, "%Y-%m-%d")

        events.append(
            {
                "title": item.get("summary", "(No title)"),
                "start": start,
                "end": end,
                "calendar": calendar_id,
                "color": item.get("colorId", "1"),
            }
        )

    return events


if __name__ == "__main__":
    for event in get_upcoming_events():
        print(f"{event['start']} — {event['title']}")
