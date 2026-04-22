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


NINE = Symbol("nine", "9", {3: 5, 4: 10, 5: 30})
TEN = Symbol("ten", "10", {3: 5, 4: 10, 5: 30})
JACK = Symbol("jack", "J", {3: 5, 4: 10, 5: 50})
QUEEN = Symbol("queen", "Q", {3: 5, 4: 10, 5: 50})
KING = Symbol("king", "K", {3: 5, 4: 10, 5: 50})

GONG = Symbol(name="gong", display="GONG", payouts={3: 5, 4: 15, 5: 75})
HOUSE = Symbol(name="house", display="HOME", payouts={3: 5, 4: 20, 5: 100})
LANTERN = Symbol(name="lantern", display="LANT", payouts={3: 5, 4: 15, 5: 75})
VASE = Symbol(name="vase", display="VASE", payouts={3: 5, 4: 15, 5: 75})

BULL = Symbol(
    name="bull",
    display="BULL",
    payouts={3: 0, 4: 0, 5: 0},
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
    payouts={},
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
