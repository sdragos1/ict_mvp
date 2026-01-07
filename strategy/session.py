import enum
import uuid
from dataclasses import dataclass
from datetime import time, datetime
from zoneinfo import ZoneInfo

from nautilus_trader.model.objects import Price


@dataclass(frozen=True)
class SessionMetadata:
    name: str
    tz: str
    open_time: time
    close_time: time

    def open_close_for(self, ts_utc: datetime) -> tuple[datetime, datetime]:
        """Return this day's session open/close in both local tz and UTC."""
        if ts_utc.tzinfo is None:
            raise ValueError("ts_utc must be timezone-aware (UTC)")

        tz = ZoneInfo(self.tz)
        local_dt = ts_utc.astimezone(tz)
        day = local_dt.date()

        open_local = datetime.combine(day, self.open_time, tzinfo=tz)
        close_local = datetime.combine(day, self.close_time, tzinfo=tz)

        open_utc = open_local.astimezone(ZoneInfo("UTC"))
        close_utc = close_local.astimezone(ZoneInfo("UTC"))
        return open_utc, close_utc

    def is_active(self, ts_utc: datetime) -> bool:
        open_utc, close_utc = self.open_close_for(ts_utc)
        return open_utc <= ts_utc < close_utc


class SessionMetadataList(enum.Enum):
    TOKYO = SessionMetadata("Tokyo", "Asia/Tokyo", time(9, 0), time(18, 0))
    LONDON = SessionMetadata("London", "Europe/London", time(8, 0), time(16, 0))
    NEW_YORK = SessionMetadata("New York", "America/New_York", time(8, 0), time(17, 0))


@dataclass
class SessionState:
    high: Price = None
    low: Price = None
    open_utc: datetime = None
    close_utc: datetime = None


class SessionEntity:
    def __init__(self, metadata: SessionMetadata, state: SessionState):
        self.id = uuid.uuid4()
        self.metadata = metadata
        self.state = state