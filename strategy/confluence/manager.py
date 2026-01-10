from nautilus_trader.model import Bar

from strategy.confluence.fvg import FairValueGap
from strategy.confluence.registry import ConfluenceRegistry
from strategy.timeframe import Timeframe


class ConfluenceManager:
    cfs: dict[Timeframe, ConfluenceRegistry]

    def __init__(self):
        self.cfs = {}

    def detect_confluences(self, tf: Timeframe, bars: list[Bar]) -> None:
        fvgs = FairValueGap.detect(bars, tf)
        if tf not in self.cfs:
            self.cfs[tf] = ConfluenceRegistry()
        self.cfs[tf].fvgs.extend(fvgs)