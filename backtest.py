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
from nautilus_trader.analysis.tearsheet import create_tearsheet
from visualization import ChartBuilder

from strategy.timeframe import Timeframe

from catalog_setup import BAR_SPEC
from strategy.history import StrategyHistory

ROOT = Path(__file__).parent
CATALOG_DIR = ROOT / "catalog"
HISTORY_PATH = ROOT / "history.json"

venue = BacktestVenueConfig(
    name="SIM",
    oms_type="NETTING",
    account_type="MARGIN",
    base_currency="USD",
    starting_balances=["1_000_000 USD"],
)

catalog = ParquetDataCatalog(CATALOG_DIR)

instruments = catalog.instruments()

bar_type = BarType(instruments[0].id, BAR_SPEC)

data = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls=Bar,
    instrument_id=instruments[0].id,
    start_time="2000-06-19",
    end_time="2000-06-24",
)


engine_config = BacktestEngineConfig(
    strategies=[
        ImportableStrategyConfig(
            strategy_path="strategy.strategy:ICTStrategy",
            config_path="strategy.strategy:ICTConfig",
            config={
                "instrument_id": instruments[0].id,
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

    chart = ChartBuilder(engine=engine, base_bar_type=bar_type, title="ICT Strategy")
    chart.add_timeframes(list(Timeframe), instruments[0].id)
    chart.add_sessions(history)
    chart.save("bars_with_fills.html")

    config = TearsheetConfig(
        charts=["bars_with_fills"],
        theme="nautilus_dark",
    )

    create_tearsheet(
        engine=engine,
        config=config,
    )
