from __future__ import annotations

from abc import ABC
from typing import TypeVar, Type

from strategy.timeframe import Timeframe

TConfluence = TypeVar("TConfluence", bound="ConfluenceBase")


class ConfluenceBase(ABC):
    name: str
    observed_tf: Timeframe
    obsolete: bool

    def __init__(
        self,
        name: str,
        observed_tf: Timeframe,
        obsolete: bool = False,
    ):
        self.name = name
        self.observed_tf = observed_tf
        self.obsolete = obsolete

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "observed_tf": self.observed_tf.value,
        }

    @classmethod
    def _parse_base(cls, data: dict) -> dict:
        """Shared parsing logic for base fields only."""
        return {
            "name": data["name"],
            "observed_tf": Timeframe(data["observed_tf"]),
            "obsolete": False,
        }

    @classmethod
    def from_dict(cls: Type[TConfluence], data: dict) -> TConfluence:
        """Factory that subclasses override or call via super()."""
        base_kwargs = cls._parse_base(data)
        return cls(**base_kwargs)
