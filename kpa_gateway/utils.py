from calendar import timegm
from datetime import UTC, datetime


EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time
HUNDREDS_OF_NANOSECONDS = 10000000


def dt_to_filetime(dt: datetime) -> int:
    if (dt.tzinfo is None) or (dt.tzinfo.utcoffset(dt) is None):
        dt = dt.replace(tzinfo=UTC)
    return EPOCH_AS_FILETIME + (timegm(dt.timetuple()) * HUNDREDS_OF_NANOSECONDS)


def filetime_to_dt(filetime_timestamp: int) -> datetime:
    return datetime.fromtimestamp((filetime_timestamp - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)
