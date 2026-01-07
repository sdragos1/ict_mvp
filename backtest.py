from pathlib import Path

from nautilus_trader.analysis import TearsheetConfig
from nautilus_trader.backtest.config import (
    BacktestVenueConfig,
    BacktestRunConfig,
    BacktestDataConfig,
)
from nautilus_trader.backtest.engine import BacktestEngineConfig, BacktestEngine
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.common.config import LoggingConfig
from nautilus_trader.model.data import BarType, Bar
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.strategy import ImportableStrategyConfig
from nautilus_trader.analysis.tearsheet import create_tearsheet, create_bars_with_fills

from catalog_setup import BAR_SPEC
from strategy.history import StrategyHistory

ROOT = Path(__file__).parent
CATALOG_DIR = ROOT / "catalog"
HISTORY_PATH = ROOT / "ict_history.json"

venue = BacktestVenueConfig(
    name="SIM",
    oms_type="NETTING",
    account_type="MARGIN",
    base_currency="USD",
    starting_balances=["1_000_000 USD"],
)

catalog = ParquetDataCatalog(CATALOG_DIR)

instruments = catalog.instruments()

data = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls=Bar,
    instrument_id=instruments[0].id,
    start_time="2000-06-19",
    end_time="2000-06-24",
)

bar_type = BarType(instruments[0].id, BAR_SPEC)


engine_config = BacktestEngineConfig(
    strategies=[
        ImportableStrategyConfig(
            strategy_path="strategy.strategy:ICTStrategy",
            config_path="strategy.strategy:ICTConfig",
            config={
                "bar_type": bar_type,
                "history_file": str(HISTORY_PATH),
            },
        )
    ],
    logging=LoggingConfig(log_level="ERROR"),
)

config = BacktestRunConfig(
    engine=engine_config,
    venues=[venue],
    data=[data],
)
node = BacktestNode(configs=[config])

if __name__ == "__main__":
    results = node.run()

    engine: BacktestEngine = node.get_engine(results[0].run_config_id)

    history = StrategyHistory.load_from_json_file(str(HISTORY_PATH))

    fig = create_bars_with_fills(
        engine=engine,
        bar_type=bar_type,
        title="ICT Strategy",
    )

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

        fig.add_vrect(
            x0=session.state.open_utc,
            x1=session.state.close_utc,
            fillcolor=color,
            layer="below",
            line_width=0,
            annotation_text=session.metadata.name,
            annotation_position="top left",
        )

        if session.state.high:
            fig.add_shape(
                type="line",
                x0=session.state.open_utc,
                y0=float(session.state.high),
                x1=session.state.close_utc,
                y1=float(session.state.high),
                line=dict(color="green", width=1, dash="dash"),
            )
        if session.state.low:
            fig.add_shape(
                type="line",
                x0=session.state.open_utc,
                y0=float(session.state.low),
                x1=session.state.close_utc,
                y1=float(session.state.low),
                line=dict(color="red", width=1, dash="dash"),
            )

    fig.write_html("bars_with_fills.html")

    config = TearsheetConfig(
        charts=["bars_with_fills"],
        theme="nautilus_dark",
    )

    create_tearsheet(
        engine=engine,
        config=config,
    )
