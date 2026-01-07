from strategy.session import SessionEntity


class StrategyHistory:
    def __init__(self):
        self.sessions: list[SessionEntity] = []

    def dump_to_json_file(self, file_path: str):
        import json

        sessions_data = []
        for session in self.sessions:
            session_data = {
                "name": session.metadata.name,
                "tz": session.metadata.tz,
                "open_time": session.metadata.open_time.isoformat(),
                "close_time": session.metadata.close_time.isoformat(),
                "state": {
                    "high": session.state.high.to_formatted_str()
                    if session.state.high
                    else None,
                    "low": session.state.low.to_formatted_str()
                    if session.state.low
                    else None,
                    "open_utc": session.state.open_utc.isoformat()
                    if session.state.open_utc
                    else None,
                    "close_utc": session.state.close_utc.isoformat()
                    if session.state.close_utc
                    else None,
                },
            }
            sessions_data.append(session_data)

        with open(file_path, "w") as f:
            json.dump(sessions_data, f, indent=4)

    @staticmethod
    def load_from_json_file(file_path: str) -> "StrategyHistory":
        import json
        from datetime import time, datetime
        from nautilus_trader.model.objects import Price
        from strategy.session import SessionMetadata, SessionState

        with open(file_path, "r") as f:
            sessions_data = json.load(f)

        history = StrategyHistory()

        history.sessions = []
        for session_data in sessions_data:
            metadata = SessionMetadata(
                name=session_data["name"],
                tz=session_data["tz"],
                open_time=time.fromisoformat(session_data["open_time"]),
                close_time=time.fromisoformat(session_data["close_time"]),
            )
            state_data = session_data["state"]
            state = SessionState(
                high=Price.from_str(state_data["high"]) if state_data["high"] else None,
                low=Price.from_str(state_data["low"]) if state_data["low"] else None,
                open_utc=datetime.fromisoformat(state_data["open_utc"])
                if state_data["open_utc"]
                else None,
                close_utc=datetime.fromisoformat(state_data["close_utc"])
                if state_data["close_utc"]
                else None,
            )
            session_entity = SessionEntity(metadata, state)
            history.sessions.append(session_entity)
        return history