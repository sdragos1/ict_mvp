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

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMetadata":
        return cls(
            name=data["name"],
            tz=data["tz"],
            open_time=time.fromisoformat(data["open_time"]),
            close_time=time.fromisoformat(data["close_time"]),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tz": self.tz,
            "open_time": self.open_time.isoformat(),
            "close_time": self.close_time.isoformat(),
        }

    def open_close_for(self, ts_utc: datetime) -> tuple[datetime, datetime]:
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

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(
            high=Price.from_str(data["high"]) if data["high"] else None,
            low=Price.from_str(data["low"]) if data["low"] else None,
            open_utc=(
                datetime.fromisoformat(data["open_utc"]) if data["open_utc"] else None
            ),
            close_utc=(
                datetime.fromisoformat(data["close_utc"]) if data["close_utc"] else None
            ),
        )

    def to_dict(self) -> dict:
        return {
            "high": self.high.to_formatted_str() if self.high else None,
            "low": self.low.to_formatted_str() if self.low else None,
            "open_utc": self.open_utc.isoformat() if self.open_utc else None,
            "close_utc": self.close_utc.isoformat() if self.close_utc else None,
        }


class SessionEntity:
    def __init__(self, metadata: SessionMetadata, state: SessionState):
        self.id = uuid.uuid4()
        self.metadata = metadata
        self.state = state

    @classmethod
    def from_dict(cls, data: dict) -> "SessionEntity":
        if "metadata" in data and "state" in data:
            # Clean recursive format
            metadata = SessionMetadata.from_dict(data["metadata"])
            state = SessionState.from_dict(data["state"])
            return cls(metadata, state)
        else:
            metadata = SessionMetadata(
                name=data["name"],
                tz=data["tz"],
                open_time=time.fromisoformat(data["open_time"]),
                close_time=time.fromisoformat(data["close_time"]),
            )
            state = SessionState.from_dict(data["state"])
            return cls(metadata, state)

    def to_dict(self) -> dict:
        return {
            "metadata": self.metadata.to_dict(),
            "state": self.state.to_dict(),
        }
