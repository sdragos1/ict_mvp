from pathlib import Path

from nautilus_trader.backtest.config import (
    BacktestVenueConfig,
    BacktestRunConfig,
    BacktestDataConfig,
)
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.common.config import LoggingConfig
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.strategy import ImportableStrategyConfig

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
    data_cls=QuoteTick,
    instrument_id=instruments[0].id,
    end_time="2020-01-10",
)

engine = BacktestEngineConfig(
    strategies=[
        ImportableStrategyConfig(
            strategy_path="strategy.strategy:ICTStrategy",
            config_path="strategy.strategy:ICTConfig",
            config={
                "instrument_id": instruments[0].id,
            },
        )
    ],
    logging=LoggingConfig(log_level="INFO"),
)

config = BacktestRunConfig(
    engine=engine,
    venues=[venue],
    data=[data],
)

node = BacktestNode(configs=[config])

node.run()
