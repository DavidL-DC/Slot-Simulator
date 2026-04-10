from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    name: str
    display: str
    payouts: dict[int, int]
    is_wild: bool = False
    is_scatter: bool = False


BULL = Symbol(name="bull", display="BULL", payouts={3: 20, 4: 50, 5: 100})
COIN = Symbol(name="coin", display="COIN", payouts={3: 15, 4: 40, 5: 80}, is_scatter=True)
YIN_YANG = Symbol(name="yin_yang", display="YIN", payouts={3: 0, 4: 0, 5: 0}, is_wild=True)
LANTERN = Symbol(name="lantern", display="LANT", payouts={3: 10, 4: 20, 5: 40})
DRUM = Symbol(name="drum", display="DRUM", payouts={3: 8, 4: 16, 5: 30})
INGOT = Symbol(name="ingot", display="GOLD", payouts={3: 5, 4: 10, 5: 20})

ALL_SYMBOLS = [
    BULL,
    COIN,
    YIN_YANG,
    LANTERN,
    DRUM,
    INGOT,
]