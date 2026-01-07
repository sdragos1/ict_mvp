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

from catalog_setup import BAR_SPEC

ROOT = Path(__file__).parent
CATALOG_DIR = ROOT / "catalog"

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
    print(engine)

    config = TearsheetConfig(
        charts=["bars_with_fills"],
        theme="nautilus_dark",
    )

    print(engine.portfolio)
    create_tearsheet(
        engine=engine,
        config=config,
        output_path=str(ROOT / "tearsheet.html"),
    )
