from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    name: str
    display: str
    payout: int
    is_wild: bool = False
    is_scatter: bool = False


BULL = Symbol(name="bull", display="BULL", payout=100)
COIN = Symbol(name="coin", display="COIN", payout=80, is_scatter=True)
YIN_YANG = Symbol(name="yin_yang", display="YIN", payout=60, is_wild=True)
LANTERN = Symbol(name="lantern", display="LANT", payout=40)
DRUM = Symbol(name="drum", display="DRUM", payout=30)
INGOT = Symbol(name="ingot", display="GOLD", payout=20)

ALL_SYMBOLS = [
    BULL,
    COIN,
    YIN_YANG,
    LANTERN,
    DRUM,
    INGOT,
]