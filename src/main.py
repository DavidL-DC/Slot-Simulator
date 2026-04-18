from config import DEFAULT_BET, START_BALANCE
from game import GameState
from ui import SlotUI


def main() -> None:
    state = GameState(
        balance=START_BALANCE,
        current_bet=DEFAULT_BET,
    )

    app = SlotUI(state)
    app.run()


if __name__ == "__main__":
    main()
