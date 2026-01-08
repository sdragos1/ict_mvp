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
        # Infer dates from sessions to align daily key levels
        # Assuming daily_key_levels corresponds to the sequence of days found in sessions
        session_dates = sorted(
            list(
                set(
                    s.state.open_utc.date()
                    for s in history.sessions
                    if s.state.open_utc
                )
            )
        )

        for i, levels in enumerate(history.daily_key_levels):
            if i >= len(session_dates):
                break

            date = session_dates[i]
            # Define time range for the day (UTC)
            start_time = datetime.combine(
                date, datetime.min.time(), tzinfo=timezone.utc
            )
            end_time = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)

            # Helper to add trace for a level
            def add_level_trace(price, name, color, dash="solid"):
                self.fig.add_trace(
                    go.Scatter(
                        x=[start_time, end_time],
                        y=[float(price), float(price)],
                        mode="lines",
                        line=dict(color=color, width=1, dash=dash),
                        name=f"{name} ({date})",
                        visible=True,  # Initially visible
                        showlegend=False,  # Clutter reduction
                        hoverinfo="name+y",
                    )
                )

            # Previous Day High/Low
            if levels.prev_day_high:
                add_level_trace(levels.prev_day_high.price, "PDH", "orange")

            if levels.prev_day_low:
                add_level_trace(levels.prev_day_low.price, "PDL", "orange")

            # H4 Levels
            for kl in levels.hour_4_high:
                add_level_trace(kl.price, f"H4 High {kl.name}", "blue", "dash")
            for kl in levels.hour_4_low:
                add_level_trace(kl.price, f"H4 Low {kl.name}", "blue", "dot")

            # H1 Levels
            for kl in levels.hour_1_high:
                add_level_trace(kl.price, f"H1 High {kl.name}", "cyan", "dash")
            for kl in levels.hour_1_low:
                add_level_trace(kl.price, f"H1 Low {kl.name}", "cyan", "dot")

    def _add_updatemenus(self):
        buttons = []
        for tf, indices in self.trace_indices.items():
            # Create visibility list: True for this TF's traces, False for others
            visible = [False] * len(self.fig.data)
            for i in indices:
                visible[i] = True

            buttons.append(
                dict(
                    label=tf.value,
                    method="update",
                    args=[
                        {"visible": visible},
                        {"title": f"Strategy Chart - {tf.value}"},
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
