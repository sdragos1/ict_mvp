from dataclasses import dataclass

from strategy.confluence.fvg import FairValueGap


@dataclass()
class ConfluenceRegistry:
    fvgs: list[FairValueGap]

    def __init__(self):
        self.fvgs = []