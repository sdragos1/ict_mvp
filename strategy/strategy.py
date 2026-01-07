from nautilus_trader.model.data import BarType, Bar
from nautilus_trader.trading.strategy import Strategy, StrategyConfig

from strategy.history import StrategyHistory
from strategy.session import (
    SessionState,
    SessionMetadataList,
    SessionMetadata,
    SessionEntity,
)


# noinspection PyDataclass
class ICTConfig(StrategyConfig):
    bar_type: BarType
    history_file: str = "ict_history.json"


class ICTStrategy(Strategy):
    def __init__(self, config: ICTConfig):
        super().__init__(config)
        self.active_sessions: dict[SessionMetadata, SessionEntity] = dict()
        self.history = StrategyHistory()

    def on_start(self):
        self.subscribe_bars(self.config.bar_type)

    def on_stop(self):
        self.unsubscribe_bars(self.config.bar_type)
        self.history.dump_to_json_file(file_path=self.config.history_file)

    def on_bar(self, bar: Bar):
        self._refresh_active_sessions()
        self._check_key_levels(bar)

    def _check_key_levels(self, bar: Bar):
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
