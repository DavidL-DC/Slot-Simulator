from dataclasses import dataclass


@dataclass
class GameState:
    balance: int
    current_bet: int
    free_spins_remaining: int = 0
    total_free_spins_won: int = 0
    collected_bulls: int = 0


def can_spin(state: GameState) -> bool:
    return state.free_spins_remaining > 0 or state.balance >= state.current_bet


def apply_bet(state: GameState) -> None:
    state.balance -= state.current_bet


def apply_win(state: GameState, win_amount: int) -> None:
    state.balance += win_amount


def set_bet(state: GameState, new_bet: int) -> bool:
    if new_bet <= 0:
        return False

    if new_bet > state.balance:
        return False

    state.current_bet = new_bet
    return True


def add_free_spins(state: GameState, amount: int) -> None:
    state.free_spins_remaining += amount
    state.total_free_spins_won += amount


def consume_free_spin(state: GameState) -> None:
    if state.free_spins_remaining > 0:
        state.free_spins_remaining -= 1


def is_free_spin(state: GameState) -> bool:
    return state.free_spins_remaining > 0
