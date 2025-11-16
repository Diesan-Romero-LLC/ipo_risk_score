import math
from typing import Dict

COEFFS_V1: Dict[str, float] = {
    "intercept": -1.2,
    "f_liq_total": 1.8,
    "f_val": 1.5,
    "f_uw": 1.0,
    "f_aud": 0.8,
    "f_geo": 0.7,
}

def logistic(z: float) -> float:
    return 100.0 / (1.0 + math.exp(-z))

def risk_score_from_features(
    features: Dict[str, float],
    coeffs: Dict[str, float] = COEFFS_V1,
) -> float:
    z = coeffs.get("intercept", 0.0)
    for name, value in features.items():
        beta = coeffs.get(name, 0.0)
        z += beta * value
    return logistic(z)