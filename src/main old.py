from config import DEFAULT_BET, PAYLINES, REELS, ROWS, START_BALANCE
from game import (
    GameState,
    add_free_spins,
    apply_bet,
    apply_win,
    can_spin,
    consume_free_spin,
    is_free_spin,
    set_bet,
    set_credits_bet,
    set_denom,
)
from slot_machine import (
    evaluate_total_win,
    print_grid,
    print_line_results,
    print_scatter_result,
    print_yin_yang_result,
    run_all_paylines_test_case,
    run_middle_row_test_case,
    run_payline_test_case,
    run_scatter_test_case,
    spin_reels,
)
from symbols import ALL_SYMBOLS
from test_grids import (
    ALL_PAYLINES_TEST_CASES,
    MIDDLE_ROW_TEST_CASES,
    PAYLINE_TEST_CASES,
    SCATTER_TEST_CASES,
)
from simulation import print_simulation_stats, run_simulation, print_balancing_summary


def print_game_info() -> None:
    print("=== Slot Simulator ===")
    print(f"Walzen: {REELS}")
    print(f"Reihen: {ROWS}")
    print(f"Startguthaben: {START_BALANCE}")
    print(f"Standard-Einsatz: {DEFAULT_BET}")
    print(f"Anzahl Linien: {len(PAYLINES)}")
    print()
    print("Symbole:")
    for symbol in ALL_SYMBOLS:
        flags = []
        if symbol.is_wild:
            flags.append("WILD")
        if symbol.is_scatter:
            flags.append("SCATTER")

        extra = f" ({', '.join(flags)})" if flags else ""
        print(f"- {symbol.display}: payouts={symbol.payouts}{extra}")


def run_all_tests() -> None:
    print("=== TESTS ===")
    print()

    passed_tests = 0
    total_tests = 0

    print("--- Tests: mittlere Reihe ---")
    print()
    for test_case in MIDDLE_ROW_TEST_CASES:
        total_tests += 1
        passed = run_middle_row_test_case(
            name=test_case["name"],
            grid=test_case["grid"],
            bet=DEFAULT_BET,
            expected_win=test_case["expected_win"],
        )
        if passed:
            passed_tests += 1

    print("--- Tests: einzelne Gewinnlinien ---")
    print()
    for test_case in PAYLINE_TEST_CASES:
        total_tests += 1
        passed = run_payline_test_case(
            name=test_case["name"],
            grid=test_case["grid"],
            payline=test_case["payline"],
            bet=DEFAULT_BET,
            expected_win=test_case["expected_win"],
        )
        if passed:
            passed_tests += 1

    print("--- Tests: Gesamtauswertung aller Linien ---")
    print()
    for test_case in ALL_PAYLINES_TEST_CASES:
        total_tests += 1
        passed = run_all_paylines_test_case(
            name=test_case["name"],
            grid=test_case["grid"],
            bet=DEFAULT_BET,
            expected_total_win=test_case["expected_total_win"],
        )
        if passed:
            passed_tests += 1

    print("--- Tests: Scatter und Freispiele ---")
    print()
    for test_case in SCATTER_TEST_CASES:
        total_tests += 1
        passed = run_scatter_test_case(
            name=test_case["name"],
            grid=test_case["grid"],
            bet=DEFAULT_BET,
            expected_scatter_count=test_case["expected_scatter_count"],
            expected_scatter_win=test_case["expected_scatter_win"],
            expected_free_spins=test_case["expected_free_spins"],
        )
        if passed:
            passed_tests += 1

    print("=== ZUSAMMENFASSUNG ===")
    print(f"{passed_tests}/{total_tests} Tests bestanden")
    print()


def play_single_round(state: GameState) -> None:
    free_spin_mode = is_free_spin(state)

    print("=== SPIELRUNDE ===")
    print(f"Aktuelles Guthaben: {state.balance}")
    print(f"Aktueller Einsatz: {state.current_bet}")
    print(f"Verbleibende Freispiele vor dem Spin: {state.free_spins_remaining}")
    print()

    if not can_spin(state):
        print("Nicht genug Guthaben für einen weiteren Spin.")
        return

    if free_spin_mode:
        consume_free_spin(state)
        print("Freispiel wird genutzt. Kein Einsatz abgezogen.")
        print(f"Verbleibende Freispiele nach Abzug: {state.free_spins_remaining}")
    else:
        apply_bet(state)
        print(f"Einsatz abgezogen. Neues Guthaben: {state.balance}")

    print()

    grid = spin_reels(state.credits_bet)
    print_grid(grid)
    print()

    win_result = evaluate_total_win(grid, state.current_bet, state.credits_bet)

    print_line_results(win_result["line_results"])
    print()
    print_scatter_result(
        win_result["scatter_count"],
        win_result["scatter_win"],
        win_result["awarded_free_spins"],
    )
    print()
    print_yin_yang_result(
        win_result["yin_yang_count"],
        win_result["yin_yang_win"],
    )
    print()
    print(f"Liniengewinn: {win_result['line_win']}")
    print(f"Scatter-Gewinn: {win_result['scatter_win']}")
    print(f"Yin-Yang-Gewinn: {win_result['yin_yang_win']}")
    print(f"Gesamtgewinn: {win_result['total_win']}")

    if win_result["awarded_free_spins"] > 0:
        add_free_spins(state, win_result["awarded_free_spins"])
        print(f"Neue Freispiele gutgeschrieben: {win_result['awarded_free_spins']}")
        print(f"Freispiele gesamt verfügbar: {state.free_spins_remaining}")

    apply_win(state, win_result["total_win"])
    print(f"Guthaben nach Auszahlung: {state.balance}")
    print()


def try_change_bet(state: GameState, user_input: str) -> bool:
    parts = user_input.split()

    if len(parts) != 2:
        return False

    command, value = parts

    if command != "bet":
        return False

    try:
        new_bet = int(value)
    except ValueError:
        print("Der Einsatz muss eine ganze Zahl sein.")
        print()
        return True

    if set_bet(state, new_bet):
        print(f"Neuer Einsatz: {state.current_bet}")
    else:
        print("Ungültiger Einsatz.")
        print(
            "Der Einsatz muss größer als 0 und kleiner oder gleich dem aktuellen Guthaben sein."
        )

    print()
    return True


def try_change_denom_or_credits(state: GameState, user_input: str) -> bool:
    parts = user_input.split()

    if len(parts) != 2:
        return False

    command, value = parts

    if command == "denom":
        try:
            new_denom = float(value)
        except ValueError:
            print("Denom muss eine Zahl sein.")
            print()
            return True

        if set_denom(state, new_denom):
            print(
                f"Neue Denom: {state.denom:.2f} | "
                f"Neuer Einsatz: {state.current_bet:.2f}"
            )
        else:
            print("Ungültige Denom oder Einsatz außerhalb der Grenzen.")

        print()
        return True

    if command == "credits":
        try:
            new_credits = int(value)
        except ValueError:
            print("Credits müssen eine ganze Zahl sein.")
            print()
            return True

        if set_credits_bet(state, new_credits):
            print(
                f"Neue Credits: {state.credits_bet} | "
                f"Neuer Einsatz: {state.current_bet:.2f}"
            )
        else:
            print("Ungültige Credits oder Einsatz außerhalb der Grenzen.")

        print()
        return True

    return False


def try_run_simulation(state: GameState, user_input: str) -> bool:
    parts = user_input.split()

    if len(parts) != 2:
        return False

    command, value = parts

    if command != "sim":
        return False

    try:
        spin_count = int(value)
    except ValueError:
        print("Die Anzahl der Spins muss eine ganze Zahl sein.")
        print()
        return True

    if spin_count <= 0:
        print("Die Anzahl der Spins muss größer als 0 sein.")
        print()
        return True

    start_balance = max(state.balance, spin_count * state.current_bet)

    print(f"Starte Simulation mit {spin_count} Basis-Spiel-Spins ...")
    print()

    stats = run_simulation(
        start_balance=start_balance,
        bet=state.current_bet,
        base_game_spins=spin_count,
        credits_bet=state.credits_bet,
        denom=state.denom,
    )

    print_balancing_summary(stats, state.credits_bet)
    print()

    return True


def run_game_loop(state: GameState) -> None:
    print("=== SPIEL STARTEN ===")
    print("Drücke Enter für einen Spin.")
    print("Gib 'bet <zahl>' ein, um den Einsatz zu ändern.")
    print("Gib 'denom <wert>' ein, um die Denom zu ändern.")
    print("Gib 'credits <zahl>' ein, um die Credits zu ändern.")
    print("Gib 'sim <anzahl>' ein, um eine Simulation zu starten.")
    print("Gib 'q' ein, um zu beenden.")
    print()

    while True:
        if not can_spin(state):
            print("Dein Guthaben reicht nicht mehr für einen weiteren Spin.")
            print("Spiel beendet.")
            break

        if is_free_spin(state):
            print(f"Freispiele aktiv: {state.free_spins_remaining}")
            print("Drücke Enter für das nächste Freispiel oder 'q' zum Beenden.")
        else:
            print(
                f"Guthaben: {state.balance:.2f} | "
                f"Einsatz: {state.current_bet:.2f} | "
                f"Denom: {state.denom:.2f} | "
                f"Credits: {state.credits_bet}"
            )

        user_input = input("> ").strip().lower()

        if user_input == "q":
            print("Spiel beendet.")
            break

        if user_input == "":
            play_single_round(state)
            continue

        if is_free_spin(state):
            print("Während Freispielen sind nur Enter oder 'q' erlaubt.")
            print()
            continue

        if try_change_bet(state, user_input):
            continue

        if try_change_denom_or_credits(state, user_input):
            continue

        if try_run_simulation(state, user_input):
            continue

        print("Ungültige Eingabe.")
        print("Erlaubt sind: Enter, 'q', oder 'bet <zahl>'.")
        print()

    print(f"Endguthaben: {state.balance}")
    print(f"Insgesamt gewonnene Freispiele: {state.total_free_spins_won}")


def main() -> None:
    """print_game_info()
    print()

    run_all_tests()

    state = GameState(balance=START_BALANCE, current_bet=DEFAULT_BET)
    run_game_loop(state)"""

    state = GameState(balance=START_BALANCE, current_bet=DEFAULT_BET, credits_bet=50)
    try_run_simulation(state, "sim 1000000")

    state = GameState(balance=START_BALANCE, current_bet=DEFAULT_BET, credits_bet=500)
    try_run_simulation(state, "sim 1000000")


if __name__ == "__main__":
    main()
