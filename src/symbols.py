from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    name: str
    display: str
    payouts: dict[int, int]
    is_wild: bool = False
    is_scatter: bool = False
    is_credit_value_symbol: bool = False
    is_collector: bool = False


NINE = Symbol("nine", "9", {3: 0, 4: 1, 5: 2})
TEN = Symbol("ten", "10", {3: 0, 4: 1, 5: 2})
JACK = Symbol("jack", "J", {3: 0, 4: 2, 5: 4})
QUEEN = Symbol("queen", "Q", {3: 1, 4: 2, 5: 5})
KING = Symbol("king", "K", {3: 1, 4: 3, 5: 6})

GONG = Symbol(name="gong", display="GONG", payouts={3: 2, 4: 5, 5: 10})
HOUSE = Symbol(name="house", display="HOME", payouts={3: 3, 4: 7, 5: 13})
LANTERN = Symbol(name="lantern", display="LANT", payouts={3: 5, 4: 9, 5: 20})
VASE = Symbol(name="vase", display="VASE", payouts={3: 7, 4: 12, 5: 30})

BULL = Symbol(
    name="bull",
    display="BULL",
    payouts={3: 15, 4: 40, 5: 80},
    is_wild=True,
)

COIN = Symbol(
    name="coin",
    display="COIN",
    payouts={},
    is_scatter=True,
)

YIN_YANG = Symbol(
    name="yin_yang",
    display="YIN",
    payouts={3: 0, 4: 0, 5: 0},
)

CREDIT = Symbol(
    name="credit",
    display="CRDT",
    payouts={},
    is_credit_value_symbol=True,
)

COLLECTOR = Symbol(
    name="collector",
    display="COLL",
    payouts={},
    is_collector=True,
)

ALL_SYMBOLS = [
    NINE,
    TEN,
    JACK,
    QUEEN,
    KING,
    GONG,
    HOUSE,
    LANTERN,
    VASE,
    BULL,
    COIN,
    YIN_YANG,
    CREDIT,
    COLLECTOR,
]
