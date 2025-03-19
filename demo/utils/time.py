from datetime import datetime, timedelta, timezone

def now() -> datetime:
    return datetime.now(timezone.utc)

def prepare_date(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def now_str() -> str:
    return prepare_date(now())



