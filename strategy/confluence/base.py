import uuid
from abc import ABC

from strategy.timeframe import Timeframe


class ConfluenceBase(ABC):
    id: uuid.UUID
    name: str
    observed_tf: Timeframe
    obsolete: bool

    def __init__(
        self,
        name: str,
        observed_tf: Timeframe,
        obsolete: bool = False,
    ):
        self.id = uuid.uuid4()
        self.name = name
        self.observed_tf = observed_tf
        self.obsolete = obsolete
