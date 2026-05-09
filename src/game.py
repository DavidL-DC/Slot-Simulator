from dataclasses import dataclass
from config import MIN_BET, AVAILABLE_DENOMS, MIN_BET, AVAILABLE_CREDITS


@dataclass
class GameState:
    balance: float
    current_bet: float
    denom: float = 0.01
    credits_bet: int = 100
    free_spins_remaining: int = 0
    total_free_spins_won: int = 0
    collected_bulls: int = 0


def recalculate_bet(state: GameState) -> None:
    state.current_bet = round(state.denom * state.credits_bet, 2)


def can_spin(state: GameState) -> bool:
    return state.free_spins_remaining > 0 or state.balance >= state.current_bet


def apply_bet(state: GameState) -> None:
    state.balance -= state.current_bet


def apply_win(state: GameState, win_amount: float) -> None:
    state.balance += win_amount


def set_bet(state: GameState, new_bet: int) -> bool:
    if new_bet <= MIN_BET:
        return False

    if new_bet > state.balance:
        return False

    state.current_bet = round(new_bet, 2)
    return True


def can_set_denom(self, denom: float) -> bool:
    return any(
        MIN_BET <= round(denom * credits, 2) <= self.balance
        for credits in AVAILABLE_CREDITS
    )


def can_set_credits(self, credits: int) -> bool:
    return any(
        MIN_BET <= round(denom * credits, 2) <= self.balance
        for denom in AVAILABLE_DENOMS
    )


def set_denom(state: GameState, new_denom: float) -> bool:
    if new_denom not in AVAILABLE_DENOMS:
        return False

    valid_credits = [
        credits
        for credits in sorted(AVAILABLE_CREDITS, reverse=True)
        if MIN_BET <= round(new_denom * credits, 2) <= state.balance
    ]

    if not valid_credits:
        return False

    state.denom = new_denom
    if state.credits_bet not in valid_credits:
        state.credits_bet = valid_credits[0]
    recalculate_bet(state)
    return True


def set_credits_bet(state: GameState, new_credits_bet: int) -> bool:
    if new_credits_bet not in AVAILABLE_CREDITS:
        return False

    valid_denoms = [
        denom
        for denom in sorted(AVAILABLE_DENOMS, reverse=True)
        if MIN_BET <= round(denom * new_credits_bet, 2) <= state.balance
    ]

    if not valid_denoms:
        return False

    state.credits_bet = new_credits_bet
    if state.denom not in valid_denoms:
        state.denom = valid_denoms[0]
    recalculate_bet(state)
    return True


def add_free_spins(state: GameState, amount: int) -> None:
    state.free_spins_remaining += amount
    state.total_free_spins_won += amount


def consume_free_spin(state: GameState) -> None:
    if state.free_spins_remaining > 0:
        state.free_spins_remaining -= 1


def is_free_spin(state: GameState) -> bool:
    return state.free_spins_remaining > 0
