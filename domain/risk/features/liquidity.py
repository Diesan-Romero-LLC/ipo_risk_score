import math
from typing import Dict

from ..entities import IpoInput

# Default configuration values. In the future these can be read from YAML.
DEFAULT_ALPHA_FREE_FLOAT = 0.7
DEFAULT_ALPHA_DOLLAR_FLOAT = 0.3
DEFAULT_LOCKUP_MAX_DAYS = 180
DEFAULT_WEIGHT_LIQUIDITY = 0.7
DEFAULT_WEIGHT_LOCKUP = 0.3


def _liquidity_core(free_float_pct: float, dollar_float: float) -> float:
    """
    Compute the core liquidity risk feature in [0, 1].

    f_liq = α1 * (1 - FF / 100) + α2 * 1 / (1 + log(1 + DV))

    where:
      - FF is the free float percentage
      - DV is the dollar value of the float (tradable portion of the deal)

    Higher values => higher liquidity risk.
    """
    ff_pct_clamped = min(max(free_float_pct, 0.0), 100.0)
    ff_component = 1.0 - ff_pct_clamped / 100.0

    safe_dollar_float = max(dollar_float, 0.0)
    dv_component = 1.0 / (1.0 + math.log1p(safe_dollar_float))

    f_liq = DEFAULT_ALPHA_FREE_FLOAT * ff_component + DEFAULT_ALPHA_DOLLAR_FLOAT * dv_component
    return max(0.0, min(f_liq, 1.0))


def _lockup_feature(lockup_days: int) -> float:
    """
    Encode lock-up risk as a value in [0, 1].

    Shorter lock-ups imply higher risk:
        f_lock = 1 - min(L, L_max) / L_max
    """
    if DEFAULT_LOCKUP_MAX_DAYS <= 0:
        return 0.0

    capped_days = min(max(lockup_days, 0), DEFAULT_LOCKUP_MAX_DAYS)
    f_lock = 1.0 - capped_days / float(DEFAULT_LOCKUP_MAX_DAYS)
    return max(0.0, min(f_lock, 1.0))


def compute_liquidity_features(ipo: IpoInput) -> Dict[str, float]:
    """
    Compute all liquidity-related features for a given IPO.

    Returns:
        - f_liq: core liquidity risk
        - f_lock: lock-up risk
        - f_liq_total: combined liquidity + lock-up feature
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
    )
    f_lock = _lockup_feature(lockup_days=ipo.deal_terms.lockup_days)

    f_liq_total = DEFAULT_WEIGHT_LIQUIDITY * f_liq + DEFAULT_WEIGHT_LOCKUP * f_lock
    f_liq_total = max(0.0, min(f_liq_total, 1.0))

    return {
        "f_liq": f_liq,
        "f_lock": f_lock,
        "f_liq_total": f_liq_total,
    }
