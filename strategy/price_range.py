from dataclasses import dataclass

from nautilus_trader.model import Price


@dataclass(frozen=True)
class PriceRange:
    min_price: Price
    max_price: Price