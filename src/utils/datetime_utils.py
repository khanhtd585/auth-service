from datetime import datetime, timezone

def get_current_datetime(tz = timezone.utc) -> datetime:
    # Get the current UTC datetime as a timezone-aware object
    return datetime.now(tz)
