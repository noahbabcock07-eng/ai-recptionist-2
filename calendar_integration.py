import os
from caldav import DAVClient, Calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ICLOUD_URL = os.environ.get("CALDAV_URL")
ICLOUD_USERNAME = os.environ.get("CALDAV_USERNAME")
ICLOUD_PASSWORD = os.environ.get("CALDAV_PASSWORD")

def create_event_in_calendar(date_str: str, time_str: str, title: str, description: str):
    """
    Create an event in the user's Apple Calendar via CalDAV.
    date_str should be 'YYYY-MM-DD', time_str should be 'HH:MM' (24h).
    """
    client = DAVClient(
        ICLOUD_URL,
        username=ICLOUD_USERNAME,
        password=ICLOUD_PASSWORD
    )
    principal = client.principal()
    calendars = principal.calendars()
    if not calendars:
        raise RuntimeError("No calendars found.")
    cal: Calendar = calendars[0]
    start = datetime.fromisoformat(f"{date_str}T{time_str}:00")
    end = start + timedelta(hours=1)
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:{start.strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{title}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""
    cal.add_event(ical)
