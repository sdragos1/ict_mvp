from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy, StrategyConfig


# noinspection PyDataclass
class ICTConfig(StrategyConfig):
    instrument_id: InstrumentId


class ICTStrategy(Strategy):
    def __init__(self, config: ICTConfig):
        super().__init__(config)
        print(config)

    def on_start(self):
        self.subscribe_quote_ticks(self.config.instrument_id)

    def on_stop(self):
        self.unsubscribe_quote_ticks(self.config.instrument_id)

    def on_quote_tick(self, tick: QuoteTick):
        print(tick)
