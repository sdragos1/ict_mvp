from nautilus_trader.model import InstrumentId
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.trading.strategy import Strategy, StrategyConfig

from strategy.history import StrategyHistory
from strategy.key_level import KeyLevels
from strategy.session import (
    SessionState,
    SessionMetadataList,
    SessionMetadata,
    SessionEntity,
)
from strategy.timeframe import Timeframe


# noinspection PyDataclass
class ICTConfig(StrategyConfig):
    instrument_id: InstrumentId
    history_file: str


class ICTStrategy(Strategy):
    def __init__(self, config: ICTConfig):
        super().__init__(config)
        self.active_sessions: dict[SessionMetadata, SessionEntity] = dict()
        self.key_levels: KeyLevels = KeyLevels()
        self.history = StrategyHistory()

        self.bar_types: dict[Timeframe, BarType] = dict()
        for tf in Timeframe:
            self.bar_types[tf] = tf.to_bar_type(config.instrument_id)
        self.bar_subs: list[BarType] = []
        for tf in Timeframe:
            if tf is Timeframe.ONE_MINUTE:
                self.bar_subs.append(tf.to_bar_type(config.instrument_id))
                continue
            self.bar_subs.append(tf.to_composite_bar_type(config.instrument_id))

    def on_start(self):
        for bt in self.bar_subs:
            self.subscribe_bars(bt)

    def on_stop(self):
        for bt in self.bar_subs:
            self.unsubscribe_bars(bt)
        self.history.dump_to_json_file(file_path=self.config.history_file)

    def on_bar(self, bar: Bar):
        if self._bar_is_tf(bar, Timeframe.ONE_HOUR):
            self._handle_hourly_bar(bar)
        if self._bar_is_tf(bar, Timeframe.ONE_DAY):
            self._handle_daily_bar(bar)

    def _handle_hourly_bar(self, bar: Bar):
        self._refresh_active_sessions()
        self._check_session_key_levels(bar)

    def _handle_daily_bar(self, bar: Bar):
        prev_day_bar = self.cache.bar(self.bar_types[Timeframe.ONE_DAY], 1)
        if prev_day_bar is not None:
            self.key_levels.prev_day_low = prev_day_bar.low
            self.key_levels.prev_day_high = prev_day_bar.high

    def _check_session_key_levels(self, bar: Bar):
        for session in self.active_sessions.values():
            if session.state.high is None or bar.high > session.state.high:
                session.state.high = bar.high
            if session.state.low is None or bar.low < session.state.low:
                session.state.low = bar.low

    def _refresh_active_sessions(self):
        now = self.clock.utc_now()
        for session_metadata in SessionMetadataList:
            if session_metadata.value.is_active(now):
                if session_metadata.value not in self.active_sessions.keys():
                    session_entity = SessionEntity(
                        session_metadata.value, SessionState()
                    )
                    session_entity.state.open_utc = now
                    self.active_sessions[session_metadata.value] = session_entity
            else:
                if session_metadata.value in self.active_sessions.keys():
                    ss_entity = self.active_sessions.pop(session_metadata.value)
                    if ss_entity not in self.history.sessions:
                        ss_entity.state.close_utc = now
                        self.history.sessions.append(ss_entity)

    def _bar_is_tf(self, bar: Bar, timeframe: Timeframe) -> bool:
        return bar.bar_type == self.bar_types[timeframe]