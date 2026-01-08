from os import PathLike
from pathlib import Path

from nautilus_trader.model.data import BarSpecification, BarAggregation, BarType
from nautilus_trader.model.enums import PriceType
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import CSVTickDataLoader
from nautilus_trader.test_kit.providers import TestInstrumentProvider


ROOT = Path(__file__).parent
CATALOG_DIR = ROOT / "catalog"
DATA_DIR = ROOT / "data"
CATALOG_DIR.mkdir(exist_ok=True)

BAR_SPEC = BarSpecification(
    step=1,
    aggregation=BarAggregation.MINUTE,
    price_type=PriceType.LAST,
)

def load_fx_hist_data(
    filename: str,
    currency: str,
    catalog_path: PathLike[str] | str,
) -> None:
    instrument = TestInstrumentProvider.default_fx_ccy(currency)
    bar_type = BarType(instrument.id, BAR_SPEC)
    wrangler = BarDataWrangler(bar_type, instrument)

    df = CSVTickDataLoader.load(
        filename, index_col=0, datetime_format="%Y%m%d %H%M%S%f", sep=";"
    )
    df.columns = [["open", "high", "low", "close", "volume"]]
    print(df)

    print("Preparing ticks...")
    ticks = wrangler.process(df)

    print("Writing data to catalog...")
    catalog = ParquetDataCatalog(catalog_path)
    catalog.write_data([instrument])
    catalog.write_data(ticks)

    print("Done")

if __name__ == "__main__":
    load_fx_hist_data(
        filename=str(DATA_DIR / "DAT_ASCII_GBPUSD_M1_2000.csv"),
        currency="GBP/USD",
        catalog_path=CATALOG_DIR,
    )