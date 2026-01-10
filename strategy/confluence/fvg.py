from enum import Enum

from nautilus_trader.model import Bar, Price

from strategy.confluence.base import ConfluenceBase
from strategy.price_range import PriceRange
from strategy.timeframe import Timeframe


class FairValueGapType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class FairValueGap(ConfluenceBase):
    range: PriceRange
    type: FairValueGapType
    related_ts: list[int]

    def __init__(
        self,
        rg: PriceRange,
        related_ts: list[int],
        tf: Timeframe,
        type: FairValueGapType,
    ):
        super().__init__("FVG", observed_tf=tf)
        self.range = rg
        self.related_ts = related_ts
        self.type = type

    @classmethod
    def detect(cls, bars: list[Bar], tf: Timeframe) -> list["FairValueGap"]:
        fvg_list: list[FairValueGap] = []
        for i in range(1, len(bars) - 1):
            prev_bar = bars[i + 1]
            curr_bar = bars[i]
            next_bar = bars[i - 1]

            if prev_bar.high < next_bar.low:
                rg = PriceRange(min_price=prev_bar.high, max_price=next_bar.low)
                fvg = FairValueGap(
                    rg,
                    related_ts=[prev_bar.ts_init, curr_bar.ts_init, next_bar.ts_init],
                    tf=tf,
                    type=FairValueGapType.BULLISH,
                )
                fvg_list.append(fvg)

            if prev_bar.low > next_bar.high:
                rg = PriceRange(min_price=next_bar.high, max_price=prev_bar.low)
                fvg = FairValueGap(
                    rg,
                    related_ts=[prev_bar.ts_init, curr_bar.ts_init, next_bar.ts_init],
                    tf=tf,
                    type=FairValueGapType.BEARISH,
                )
                fvg_list.append(fvg)

        return fvg_list

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "range": {
                    "min": str(self.range.min_price),
                    "max": str(self.range.max_price),
                },
                "type": self.type.value,
                "related_ts": [b for b in self.related_ts],
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "FairValueGap":
        base_kwargs = cls._parse_base(data)

        min_price = Price.from_str(data["range"]["min"])
        max_price = Price.from_str(data["range"]["max"])

        rg = PriceRange(min_price=min_price, max_price=max_price)
        type_ = FairValueGapType(data["type"])
        related_ts = [b for b in data["related_ts"]]
        return cls(rg, related_ts, base_kwargs["observed_tf"], type_)
