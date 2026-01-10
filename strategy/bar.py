from nautilus_trader.model import Bar


def bar_is_up(bar: Bar) -> bool:
    return bar.close > bar.open


def bar_is_down(bar: Bar) -> bool:
    return bar.close < bar.open


def bar_is_high(prev_bar: Bar, bar: Bar) -> bool:
    return bar_is_up(prev_bar) and bar_is_down(bar)


def bar_is_low(prev_bar: Bar, bar: Bar) -> bool:
    return bar_is_down(prev_bar) and bar_is_up(bar)


def bar_max_high(bar1: Bar, bar2: Bar) -> Bar:
    return bar1 if bar1.high >= bar2.high else bar2


def bar_min_low(bar1: Bar, bar2: Bar) -> Bar:
    return bar1 if bar1.low <= bar2.low else bar2