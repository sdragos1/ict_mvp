from dataclasses import dataclass

from nautilus_trader.model import Price


@dataclass(frozen=True)
class KeyLevel:
    price: Price
    name: str
    touched: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "KeyLevel":
        return cls(
            price=Price.from_str(data["price"]),
            name=data["name"],
            touched=data["touched"],
        )

    def to_dict(self) -> dict:
        return {
            "price": self.price.to_formatted_str(),
            "name": self.name,
            "touched": self.touched,
        }


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

    @classmethod
    def from_dict(cls, data: dict) -> "KeyLevels":
        instance = cls()
        instance.hour_4_high = [
            KeyLevel.from_dict(d) for d in data.get("hour_4_high", [])
        ]
        instance.hour_4_low = [
            KeyLevel.from_dict(d) for d in data.get("hour_4_low", [])
        ]
        instance.hour_1_high = [
            KeyLevel.from_dict(d) for d in data.get("hour_1_high", [])
        ]
        instance.hour_1_low = [
            KeyLevel.from_dict(d) for d in data.get("hour_1_low", [])
        ]

        if data.get("prev_day_high"):
            instance.prev_day_high = KeyLevel.from_dict(data["prev_day_high"])

        if data.get("prev_day_low"):
            instance.prev_day_low = KeyLevel.from_dict(data["prev_day_low"])

        return instance

    def to_dict(self) -> dict:
        return {
            "hour_4_high": [kl.to_dict() for kl in self.hour_4_high],
            "hour_4_low": [kl.to_dict() for kl in self.hour_4_low],
            "hour_1_high": [kl.to_dict() for kl in self.hour_1_high],
            "hour_1_low": [kl.to_dict() for kl in self.hour_1_low],
            "prev_day_high": (
                self.prev_day_high.to_dict() if self.prev_day_high else None
            ),
            "prev_day_low": self.prev_day_low.to_dict() if self.prev_day_low else None,
        }
