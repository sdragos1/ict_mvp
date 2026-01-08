from strategy.key_level import KeyLevels
from strategy.session import SessionEntity


class StrategyHistory:
    def __init__(self):
        self.sessions: list[SessionEntity] = []
        self.daily_key_levels: list[KeyLevels] = []

    def dump_to_json_file(self, file_path: str):
        import json

        data = {
            "sessions": [session.to_dict() for session in self.sessions],
            "daily_key_levels": [levels.to_dict() for levels in self.daily_key_levels],
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_json_file(file_path: str) -> "StrategyHistory":
        import json
        from strategy.session import SessionEntity
        from strategy.key_level import KeyLevels

        with open(file_path, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            sessions_data = data
            key_levels_data = []
        else:
            sessions_data = data.get("sessions", [])
            key_levels_data = data.get("daily_key_levels", [])

        history = StrategyHistory()

        history.sessions = []
        for session_data in sessions_data:
            history.sessions.append(SessionEntity.from_dict(session_data))

        history.daily_key_levels = []
        for levels_data in key_levels_data:
            history.daily_key_levels.append(KeyLevels.from_dict(levels_data))

        return history
