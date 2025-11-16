import math
from typing import Dict

# Heuristic coefficients for model version v1.
# These should be calibrated with historical data.
COEFFS_V1: Dict[str, float] = {
    "intercept": -0.5,
    "f_liq_total": 2.0,
    "f_val": 1.0,
    "f_uw": 1.5,
    "f_aud": 1.5,
    "f_geo": 1.0,
}

LOGIT_CLIP = 30.0  # protects against overflow in exp()

# Safe bounds for feature values; features are expected to be in [0, 1]
# but we allow some slack to tolerate small numerical noise.
FEATURE_MIN_SAFE = -1.0
FEATURE_MAX_SAFE = 2.0


def _logistic(z: float) -> float:
    """
    Numerically stable logistic function.

    Clips z to [-LOGIT_CLIP, LOGIT_CLIP] to avoid overflow when computing exp(-z).
    """
    if not math.isfinite(z):
        raise ValueError(f"Non-finite logit value: {z!r}")

    z_clipped = max(-LOGIT_CLIP, min(z, LOGIT_CLIP))
    return 1.0 / (1.0 + math.exp(-z_clipped))


def _validate_feature_value(name: str, value: float) -> None:
    """
    Ensure feature values are finite and within a safe range.

    This is defensive: it protects the scoring function from being fed arbitrarily
    large values if the caller bypasses the standard feature builder.
    """
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

    Unknown feature keys in `features` are ignored, but each value is validated
    to be finite and within a safe numeric range.
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
    # Risk higher when logistic probability is higher.
    return 100.0 * p
