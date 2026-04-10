from config import DEFAULT_BET, REELS, ROWS, START_BALANCE
from symbols import ALL_SYMBOLS


def print_game_info() -> None:
    print("=== Slot Simulator ===")
    print(f"Walzen: {REELS}")
    print(f"Reihen: {ROWS}")
    print(f"Startguthaben: {START_BALANCE}")
    print(f"Standard-Einsatz: {DEFAULT_BET}")
    print()
    print("Symbole:")
    for symbol in ALL_SYMBOLS:
        flags = []
        if symbol.is_wild:
            flags.append("WILD")
        if symbol.is_scatter:
            flags.append("SCATTER")

        extra = f" ({', '.join(flags)})" if flags else ""
        print(f"- {symbol.display}: payout={symbol.payout}{extra}")


def main() -> None:
    print_game_info()


if __name__ == "__main__":
    main()