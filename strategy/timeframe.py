import enum

from nautilus_trader.model import BarType, InstrumentId


class Timeframe(enum.Enum):
    ONE_MINUTE = "1-MINUTE"
    FIVE_MINUTE = "5-MINUTE"
    FIFTEEN_MINUTE = "15-MINUTE"
    ONE_HOUR = "1-HOUR"
    FOUR_HOUR = "4-HOUR"
    ONE_DAY = "1-DAY"

    def to_composite_bar_type(self, instrument_id: InstrumentId) -> BarType:
        return BarType.from_str(
            f"{instrument_id}-{self.value}-LAST-INTERNAL@1-MINUTE-EXTERNAL"
        )

    def to_bar_type(self, instrument_id: InstrumentId) -> BarType:
        agg_src = "INTERNAL" if self in INTERNAL_AGG_TF else "EXTERNAL"
        return BarType.from_str(f"{instrument_id}-{self.value}-LAST-{agg_src}")


EXTERNAL_AGG_TF = [Timeframe.ONE_MINUTE]
INTERNAL_AGG_TF = [
    Timeframe.FIVE_MINUTE,
    Timeframe.FIFTEEN_MINUTE,
    Timeframe.ONE_HOUR,
    Timeframe.FOUR_HOUR,
    Timeframe.ONE_DAY,
]