from dataclasses import dataclass


@dataclass
class GameState:
    balance: int
    current_bet: int


def can_spin(state: GameState) -> bool:
    return state.balance >= state.current_bet


def apply_bet(state: GameState) -> None:
    state.balance -= state.current_bet


def apply_win(state: GameState, win_amount: int) -> None:
    state.balance += win_amount