from nautilus_trader.model import Bar

from strategy.confluence.fvg import FairValueGap
from strategy.confluence.registry import ConfluenceRegistry
from strategy.timeframe import Timeframe


class ConfluenceManager:
    confluences: dict[Timeframe, ConfluenceRegistry]

    def __init__(self):
        self.confluences = {}
        self.init_confluences()

    def init_confluences(self):
        for tf in Timeframe:
            self.confluences[tf] = ConfluenceRegistry()

    def detect_confluences(self, tf: Timeframe, bars: list[Bar]) -> None:
        fvgs = FairValueGap.detect(bars, tf)
        self.confluences[tf].add_fvgs(fvgs)