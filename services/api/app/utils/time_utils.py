from datetime import datetime, timezone

def get_current_timestamp() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def add_seconds(timestamp: int, seconds: int) -> int:
    return timestamp + (seconds * 1000)

def add_days(timestamp: int, days: int) -> int:
    return timestamp + (days * 24 * 60 * 60 * 1000)

def get_hour_boundary(timestamp: int) -> int:
    return (timestamp // (60 * 60 * 1000)) * (60 * 60 * 1000)