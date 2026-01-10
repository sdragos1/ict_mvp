from strategy.confluence.registry import ConfluenceRegistry
import json
from strategy.session import SessionEntity
from strategy.key_level import KeyLevels
from strategy.timeframe import Timeframe


class StrategyHistory:
    def __init__(self):
        self.sessions: list[SessionEntity] = []
        self.daily_key_levels: list[KeyLevels] = []
        self.daily_confluences: list[dict[Timeframe, ConfluenceRegistry]] = []

    def dump_to_json_file(self, file_path: str):
        import json

        data = {
            "sessions": [session.to_dict() for session in self.sessions],
            "daily_key_levels": [levels.to_dict() for levels in self.daily_key_levels],
            "daily_confluences": [
                {tf.value: registry.to_dict() for tf, registry in confluences.items()}
                for confluences in self.daily_confluences
            ],
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_json_file(file_path: str) -> "StrategyHistory":
        with open(file_path, "r") as f:
            data = json.load(f)

        if isinstance(data, list):
            sessions_data = data
            key_levels_data = []
            confluences_data = []
        else:
            sessions_data = data.get("sessions", [])
            key_levels_data = data.get("daily_key_levels", [])
            confluences_data = data.get("daily_confluences", [])

        history = StrategyHistory()

        history.sessions = []
        for session_data in sessions_data:
            history.sessions.append(SessionEntity.from_dict(session_data))

        history.daily_key_levels = []
        for levels_data in key_levels_data:
            history.daily_key_levels.append(KeyLevels.from_dict(levels_data))

        history.daily_confluences = []
        for day_data in confluences_data:
            day_confluences = {}
            for tf_value, registry_data in day_data.items():
                tf = Timeframe(tf_value)
                registry = ConfluenceRegistry.from_dict(registry_data)
                day_confluences[tf] = registry
            history.daily_confluences.append(day_confluences)

        return history
