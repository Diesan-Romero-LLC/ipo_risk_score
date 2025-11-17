import math
from typing import Dict

# Heuristic coefficients for model version v1.
# These should be calibrated with historical data. They represent a
# reasonable starting point if no other calibration is available.
COEFFS_V1: Dict[str, float] = {
    "intercept": -0.5,
    # Combined liquidity risk (liquidity + lock‑up).  Liquidity is
    # considered a primary driver of ex‑ante IPO risk.
    "f_liq_total": 2.0,
    # Relative valuation premium.  A higher premium implies
    # relatively expensive pricing and therefore higher risk.
    "f_val": 1.0,
    # Underwriter quality.  Lower tier underwriters (higher f_uw) add risk.
    "f_uw": 1.5,
    # Auditor quality.  Non‑Big4 auditors add risk.
    "f_aud": 1.5,
    # Sector/geographic context.
    "f_geo": 1.0,
    # Financial strength.  Higher values indicate weaker profitability or
    # growth and thus higher risk.  Included with weight 1.0 by default.
    "f_fin": 1.0,
}

# Example coefficients derived from the formulas presented in the
# ipo_risk_score.tex document.  These values mirror the relative
# importance of each feature as described in the paper.
COEFFS_TEX_EXAMPLE: Dict[str, float] = {
    "intercept": -0.5,
    "f_liq_total": 2.0,
    "f_val": 2.0,
    "f_uw": 1.5,
    "f_aud": 1.5,
    "f_geo": 1.0,
    # Financial strength weight (moderate).
    "f_fin": 1.0,
}

LOGIT_CLIP = 30.0  # protects against overflow in exp()
FEATURE_MIN_SAFE = -1.0
FEATURE_MAX_SAFE = 2.0


def _logistic(z: float) -> float:
    """Numerically stable logistic function."""
    if not math.isfinite(z):
        raise ValueError(f"Non-finite logit value: {z!r}")
    z_clipped = max(-LOGIT_CLIP, min(z, LOGIT_CLIP))
    return 1.0 / (1.0 + math.exp(-z_clipped))


def _validate_feature_value(name: str, value: float) -> None:
    """Ensure feature values are finite and within a safe range."""
    if not math.isfinite(value):
        raise ValueError(f"Feature {name!r} is non-finite: {value!r}")
    if value < FEATURE_MIN_SAFE or value > FEATURE_MAX_SAFE:
        raise ValueError(
            f"Feature {name!r} has suspicious value {value!r}; "
            f"expected in [{FEATURE_MIN_SAFE}, {FEATURE_MAX_SAFE}]"
        )


def risk_score_from_features(features: Dict[str, float], coeffs: Dict[str, float]) -> float:
    """
    Compute a bounded risk score in [0, 100] from a normalized feature dict.
    Unknown feature keys in `features` are ignored, but each value is validated.
    """
    intercept = float(coeffs.get("intercept", 0.0))
    z = intercept
    for name, raw_value in features.items():
        value = float(raw_value)
        _validate_feature_value(name, value)
        if name not in coeffs:
            continue
        z += float(coeffs[name]) * value
    p = _logistic(z)
    return 100.0 * p
