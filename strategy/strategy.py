import pandas as pd
from nautilus_trader.core.nautilus_pyo3 import (
    ForexSession,
    fx_next_end,
    fx_prev_end,
    fx_prev_start,
)
from nautilus_trader.model.data import BarType, Bar
from nautilus_trader.trading.strategy import Strategy, StrategyConfig

from strategy.session import SessionKeyLevels, Sessions, Session


# noinspection PyDataclass
class ICTConfig(StrategyConfig):
    bar_type: BarType


class ICTStrategy(Strategy):
    def __init__(self, config: ICTConfig):
        super().__init__(config)
        # self.session_states: dict[Sessions, SessionKeyLevels] = {
        #     ForexSession.SYDNEY: SessionKeyLevels(),
        #     ForexSession.TOKYO: SessionKeyLevels(),
        #     ForexSession.LONDON: SessionKeyLevels(),
        #     ForexSession.NEW_YORK: SessionKeyLevels(),
        # }
        self.curr_sessions: set[Session] = set()
        self.dow: int = -1

    def on_start(self):
        self.subscribe_bars(self.config.bar_type)
        self._refresh_curr_fx_session()
        self.dow = self.clock.utc_now().weekday()

    def on_stop(self):
        self.unsubscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar):
        pass

    def _refresh_curr_fx_session(self):
        now_ts = self.clock.timestamp_ns()
        now = pd.to_datetime(now_ts, utc=True)
        for session in Sessions:
            if session.value.is_active(now):
                self.curr_sessions.add(session.value)
            else:
                self.curr_sessions.discard(session.value)
        print(self.curr_sessions)

