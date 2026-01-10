from datetime import datetime, timezone
import plotly.graph_objects as go
from nautilus_trader.model import InstrumentId
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.analysis.tearsheet import create_bars_with_fills
from nautilus_trader.backtest.engine import BacktestEngine
from strategy.timeframe import Timeframe
from strategy.history import StrategyHistory


class ChartBuilder:
    def __init__(
        self,
        engine: BacktestEngine,
        base_bar_type: BarType,
        title: str = "Strategy Chart",
    ):
        self.engine = engine
        self.base_bar_type = base_bar_type
        self.fig = create_bars_with_fills(
            engine=engine,
            bar_type=base_bar_type,
            title=title,
        )
        # Dictionary to keep track of trace indices for each timeframe
        # The default 1-minute traces are already added by create_bars_with_fills
        self.trace_indices = {Timeframe.ONE_MINUTE: list(range(len(self.fig.data)))}
        self.key_level_indices = []

    def add_timeframes(self, timeframes: list[Timeframe], instrument_id: InstrumentId):
        for tf in timeframes:
            if tf == Timeframe.ONE_MINUTE:
                continue

            bt = tf.to_bar_type(instrument_id)

            # Fetch bars from the engine
            bars: list[Bar] = []
            if hasattr(self.engine, "cache"):
                try:
                    bars = self.engine.cache.bars(bt)
                except Exception as e:
                    print(f"Failed to get bars from engine.cache for {tf}: {e}")

            if not bars:
                print(f"No bars found for {tf.value}")
                continue

            # Extract data
            opens = [float(b.open) for b in bars]
            highs = [float(b.high) for b in bars]
            lows = [float(b.low) for b in bars]
            closes = [float(b.close) for b in bars]

            times = [
                datetime.fromtimestamp(b.ts_init / 1_000_000_000, tz=timezone.utc)
                for b in bars
            ]

            # Add trace
            self.fig.add_trace(
                go.Candlestick(
                    x=times,
                    open=opens,
                    high=highs,
                    low=lows,
                    close=closes,
                    name=tf.value,
                    visible=False,
                )
            )

            self.trace_indices[tf] = [len(self.fig.data) - 1]

    def add_sessions(self, history: StrategyHistory):
        for session in history.sessions:
            if not session.state.open_utc or not session.state.close_utc:
                continue

            color = "rgba(0, 0, 255, 0.1)"
            if session.metadata.name == "Tokyo":
                color = "rgba(255, 0, 0, 0.1)"
            elif session.metadata.name == "London":
                color = "rgba(0, 255, 0, 0.1)"
            elif session.metadata.name == "New York":
                color = "rgba(0, 0, 255, 0.1)"

            self.fig.add_vrect(
                x0=session.state.open_utc,
                x1=session.state.close_utc,
                fillcolor=color,
                layer="below",
                line_width=0,
                annotation_text=session.metadata.name,
                annotation_position="top left",
            )

            if session.state.high:
                self.fig.add_shape(
                    type="line",
                    x0=session.state.open_utc,
                    y0=float(session.state.high),
                    x1=session.state.close_utc,
                    y1=float(session.state.high),
                    line=dict(color="green", width=1, dash="dash"),
                )
            if session.state.low:
                self.fig.add_shape(
                    type="line",
                    x0=session.state.open_utc,
                    y0=float(session.state.low),
                    x1=session.state.close_utc,
                    y1=float(session.state.low),
                    line=dict(color="red", width=1, dash="dash"),
                )

    def add_key_levels(self, history: StrategyHistory):
        from datetime import timedelta

        # Helper to map Timeframe to timedelta duration
        def get_duration(tf_value):
            if tf_value == "1-MINUTE":
                return timedelta(minutes=1)
            elif tf_value == "5-MINUTE":
                return timedelta(minutes=5)
            elif tf_value == "15-MINUTE":
                return timedelta(minutes=15)
            elif tf_value == "1-HOUR":
                return timedelta(hours=1)
            elif tf_value == "4-HOUR":
                return timedelta(hours=4)
            elif tf_value == "1-DAY":
                return timedelta(days=1)
            return timedelta(hours=1)  # Default fallback

        # Aggregate data by (name, timeframe_value) to create single traces
        # structure: key -> {x: [], y: [], color: str}
        aggregated_data = {}

        def collect_level(kl, color):
            if not getattr(kl, "ts", None):
                return

            key = (kl.name, kl.observed_tf.value)
            if key not in aggregated_data:
                aggregated_data[key] = {"x": [], "y": [], "color": color}

            start_time = datetime.fromtimestamp(kl.ts / 1_000_000_000, tz=timezone.utc)
            duration = get_duration(kl.observed_tf.value)
            end_time = start_time + duration

            # Add segment followed by None to break the line
            aggregated_data[key]["x"].extend([start_time, end_time, None])
            aggregated_data[key]["y"].extend([float(kl.price), float(kl.price), None])

        for levels in history.daily_key_levels:
            # Previous Day High/Low
            if levels.prev_day_high:
                collect_level(levels.prev_day_high, "orange")
            if levels.prev_day_low:
                collect_level(levels.prev_day_low, "orange")

            # H4 Levels
            for kl in levels.hour_4_high:
                collect_level(kl, "blue")
            for kl in levels.hour_4_low:
                collect_level(kl, "blue")

            # H1 Levels
            for kl in levels.hour_1_high:
                collect_level(kl, "magenta")
            for kl in levels.hour_1_low:
                collect_level(kl, "magenta")

        # Create traces from aggregated data
        for (name, tf_value), data in aggregated_data.items():
            self.fig.add_trace(
                go.Scatter(
                    x=data["x"],
                    y=data["y"],
                    mode="lines",
                    line=dict(color=data["color"], width=2),
                    name=f"{name} ({tf_value})",
                    visible=True,
                    showlegend=True,
                    hoverinfo="name+y+x",
                    connectgaps=False,  # Ensure gaps are respected
                )
            )
            self.key_level_indices.append(len(self.fig.data) - 1)

    def _add_updatemenus(self):
        buttons = []

        # Collect all indices that belong to Timeframe traces
        all_tf_indices = []
        for indices in self.trace_indices.values():
            all_tf_indices.extend(indices)
        all_tf_indices.sort()

        for tf, indices in self.trace_indices.items():
            # Create visibility list ONLY for the timeframe traces
            # The length and order must match 'all_tf_indices' which we will pass as the 'traces' arg

            # Map global index to boolean
            # We want True if global index is in 'indices' (current tf), False otherwise (other tfs)
            visible_status = []
            for global_idx in all_tf_indices:
                if global_idx in indices:
                    visible_status.append(True)
                else:
                    visible_status.append(False)

            buttons.append(
                dict(
                    label=tf.value,
                    method="update",
                    args=[
                        {"visible": visible_status},
                        {"title": f"Strategy Chart - {tf.value}"},
                        all_tf_indices,  # Traces to apply 'visible' to
                    ],
                )
            )

        self.fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    buttons=buttons,
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=1.0,
                    xanchor="left",
                    y=1.15,
                    yanchor="top",
                ),
            ]
        )

    def save(self, filename: str):
        self._add_updatemenus()
        self.fig.write_html(filename)
