from typing import Dict, List, Optional

from .entities import IpoInput, RiskDriverDomain, RiskResult
from .features import build_feature_vector
from .logistic import COEFFS_V1, risk_score_from_features
from .validators import validate_ipo_input

MODEL_VERSION = "v1-logistic"


def compute_ipo_risk(
    ipo: IpoInput,
    *,
    coeffs: Optional[Dict[str, float]] = None,
    model_version: Optional[str] = None,
    include_attractiveness: bool = True,
) -> RiskResult:
    """
    Validate IPO input, build feature vector, compute logit-based risk and return RiskResult.

    Parameters:
      coeffs: optional coefficients overriding the defaults.
      model_version: optional version string.
      include_attractiveness: if False, the attractiveness percent is set to None.
    """
    validate_ipo_input(ipo)
    features = build_feature_vector(ipo)
    coeffs_to_use = coeffs if coeffs is not None else COEFFS_V1
    risk = risk_score_from_features(features, coeffs_to_use)
    # Optionally compute attractiveness (100 - risk); can be disabled.
    attractiveness = 100.0 - risk if include_attractiveness else None

    drivers: List[RiskDriverDomain] = []
    for name, value in features.items():
        drivers.append(
            RiskDriverDomain(
                name=name,
                contribution_points=round(100 * value, 1),
                description=f"Normalized feature {name} = {value:.2f}",
            )
        )

    return RiskResult(
        risk_score=risk,
        attractiveness_percent=attractiveness,
        model_version=model_version if model_version is not None else MODEL_VERSION,
        drivers=drivers,
        raw_features=features,
    )
