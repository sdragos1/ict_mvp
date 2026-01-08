from dataclasses import dataclass

from nautilus_trader.model import Price


@dataclass(frozen=True)
class KeyLevel:
    price: Price
    name: str
    touched: bool = False


@dataclass()
class KeyLevels:
    hour_4_high: list[KeyLevel]
    hour_4_low: list[KeyLevel]
    hour_1_high: list[KeyLevel]
    hour_1_low: list[KeyLevel]
    prev_day_high: KeyLevel | None
    prev_day_low: KeyLevel | None

    def __init__(self):
        self.hour_4_high = []
        self.hour_4_low = []
        self.hour_1_high = []
        self.hour_1_low = []
        self.prev_day_high = None
        self.prev_day_low = None