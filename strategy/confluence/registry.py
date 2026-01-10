from dataclasses import dataclass

from strategy.confluence.fvg import FairValueGap


@dataclass()
class ConfluenceRegistry:
    fvgs: list[FairValueGap]

    def __init__(self):
        self.fvgs = list()

    def add_fvgs(self, fvgs: list[FairValueGap]):
        for fvg in fvgs:
            if fvg.related_ts not in [existing.related_ts for existing in self.fvgs]:
                self.fvgs.append(fvg)

    def to_dict(self) -> dict:
        return {"fvgs": [fvg.to_dict() for fvg in self.fvgs]}

    @classmethod
    def from_dict(cls, data: dict):
        registry = cls()
        registry.fvgs = list([FairValueGap.from_dict(d) for d in data.get("fvgs", [])])
        return registry
