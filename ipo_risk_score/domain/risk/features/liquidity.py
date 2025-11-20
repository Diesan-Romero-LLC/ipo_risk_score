import math
from typing import Dict

from ..entities import IpoInput

# Default configuration values.
DEFAULT_ALPHA_FREE_FLOAT = 0.7
DEFAULT_ALPHA_DOLLAR_FLOAT = 0.3
DEFAULT_LOCKUP_MAX_DAYS = 180
DEFAULT_WEIGHT_LIQUIDITY = 0.7
DEFAULT_WEIGHT_LOCKUP = 0.3


def _liquidity_core(
    free_float_pct: float,
    dollar_float: float,
    *,
    alpha_free_float: float = DEFAULT_ALPHA_FREE_FLOAT,
    alpha_dollar_float: float = DEFAULT_ALPHA_DOLLAR_FLOAT,
) -> float:
    """
    Core liquidity risk: α1 * (1 - FF/100) + α2 * 1/(1 + log(1 + DV)).
    Weights α1, α2 can be overridden.
    """
    ff_pct_clamped = min(max(free_float_pct, 0.0), 100.0)
    ff_component = 1.0 - ff_pct_clamped / 100.0
    safe_dollar_float = max(dollar_float, 0.0)
    dv_component = 1.0 / (1.0 + math.log1p(safe_dollar_float))
    f_liq = alpha_free_float * ff_component + alpha_dollar_float * dv_component
    return max(0.0, min(f_liq, 1.0))


def _lockup_feature(lockup_days: int, *, lockup_max_days: int = DEFAULT_LOCKUP_MAX_DAYS) -> float:
    """
    Lock‑up risk: 1 - min(L, L_max)/L_max. L_max defaults to 180 days but is configurable.
    """
    if lockup_max_days <= 0:
        return 0.0
    capped_days = min(max(lockup_days, 0), lockup_max_days)
    f_lock = 1.0 - capped_days / float(lockup_max_days)
    return max(0.0, min(f_lock, 1.0))


def compute_liquidity_features(
    ipo: IpoInput,
    *,
    alpha_free_float: float = DEFAULT_ALPHA_FREE_FLOAT,
    alpha_dollar_float: float = DEFAULT_ALPHA_DOLLAR_FLOAT,
    lockup_max_days: int = DEFAULT_LOCKUP_MAX_DAYS,
    weight_liquidity: float = DEFAULT_WEIGHT_LIQUIDITY,
    weight_lockup: float = DEFAULT_WEIGHT_LOCKUP,
) -> Dict[str, float]:
    """
    Compute liquidity-related features with configurable weights.
    Returns a dict with f_liq, f_lock and f_liq_total.
    """
    offer_mid = (ipo.deal_terms.price_low + ipo.deal_terms.price_high) / 2.0
    offer_usd = offer_mid * ipo.deal_terms.offer_shares
    free_float_fraction = min(
        max(ipo.deal_terms.free_float_pct, 0.0) / 100.0,
        1.0,
    )
    dollar_float = offer_usd * free_float_fraction
    f_liq = _liquidity_core(
        free_float_pct=ipo.deal_terms.free_float_pct,
        dollar_float=dollar_float,
        alpha_free_float=alpha_free_float,
        alpha_dollar_float=alpha_dollar_float,
    )
    f_lock = _lockup_feature(
        lockup_days=ipo.deal_terms.lockup_days,
        lockup_max_days=lockup_max_days,
    )
    f_liq_total = weight_liquidity * f_liq + weight_lockup * f_lock
    f_liq_total = max(0.0, min(f_liq_total, 1.0))
    return {
        "f_liq": f_liq,
        "f_lock": f_lock,
        "f_liq_total": f_liq_total,
    }
