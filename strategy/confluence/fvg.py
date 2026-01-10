from enum import Enum

from nautilus_trader.model import Bar

from strategy.confluence.base import ConfluenceBase
from strategy.price_range import PriceRange
from strategy.timeframe import Timeframe


class FairValueGapType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class FairValueGap(ConfluenceBase):
    range: PriceRange
    type: FairValueGapType
    related_bars: list[Bar]

    def __init__(
        self,
        rg: PriceRange,
        related_bars: list[Bar],
        tf: Timeframe,
        type: FairValueGapType,
    ):
        super().__init__("FVG", observed_tf=tf)
        self.range = rg
        self.related_bars = related_bars
        self.type = type

    @classmethod
    def detect(cls, bars: list[Bar], tf: Timeframe) -> list['FairValueGap']:
        fvg_list: list[FairValueGap] = []
        for i in range(1, len(bars) - 1):
            prev_bar = bars[i - 1]
            curr_bar = bars[i]
            next_bar = bars[i + 1]

            if prev_bar.high < next_bar.low:
                rg = PriceRange(min_price=prev_bar.high, max_price=next_bar.low)
                fvg = FairValueGap(
                    rg,
                    related_bars=[prev_bar, curr_bar, next_bar],
                    tf=tf,
                    type=FairValueGapType.BULLISH,
                )
                fvg_list.append(fvg)

            if prev_bar.low > next_bar.high:
                rg = PriceRange(min_price=next_bar.high, max_price=prev_bar.low)
                fvg = FairValueGap(
                    rg,
                    related_bars=[prev_bar, curr_bar, next_bar],
                    tf=tf,
                    type=FairValueGapType.BEARISH,
                )
                fvg_list.append(fvg)

        return fvg_list
