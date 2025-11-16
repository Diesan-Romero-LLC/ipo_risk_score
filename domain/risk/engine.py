from .entities import IpoInput, RiskDriverDomain, RiskResult
from .features import build_feature_vector
from .logistic import COEFFS_V1, risk_score_from_features
from .validators import validate_ipo_input

MODEL_VERSION = "v1-logistic"


def compute_ipo_risk(ipo: IpoInput) -> RiskResult:
    """
    High-level API: validate IPO input, compute features, score risk, and
    return a rich RiskResult object.
    """
    # Defensive validation of input.
    validate_ipo_input(ipo)

    features = build_feature_vector(ipo)
    risk = risk_score_from_features(features, COEFFS_V1)
    attractiveness = 100.0 - risk

    drivers = []
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
        model_version=MODEL_VERSION,
        drivers=drivers,
        raw_features=features,
    )
