from typing import Dict, List, Optional

from .entities import IpoInput, RiskDriverDomain, RiskResult
from .features import build_feature_vector
from .logistic import COEFFS_V1, risk_score_from_features
from .validators import validate_ipo_input

# Default model version and coefficient set.  Users can provide custom
# coefficients when calling `compute_ipo_risk` to override this.
MODEL_VERSION = "v1-logistic"


def compute_ipo_risk(
    ipo: IpoInput,
    *,
    coeffs: Optional[Dict[str, float]] = None,
    model_version: Optional[str] = None,
    include_attractiveness: bool = True,
    prospectus_text: Optional[str] = None,
) -> RiskResult:
    """
    High-level API: validate IPO input, compute features, score risk, and
    return a rich RiskResult object.

    Parameters
    ----------
    ipo:
        The IPO input object containing deal terms, financial snapshot and
        categorical attributes.
    coeffs:
        Optional dictionary mapping feature keys to logistic coefficients.
        If provided, these coefficients will be used instead of the default
        `COEFFS_V1`.  This allows callers to supply the example coefficients
        from the paper (`COEFFS_TEX_EXAMPLE`) or any calibrated set.
    model_version:
        Optional string identifying the version of the model used.  If
        omitted, the global `MODEL_VERSION` is used.

    Returns
    -------
    RiskResult
        An object containing the risk score, attractiveness percentage,
        version string, driver breakdown and raw feature vector.
    """
    # Defensive validation of input.
    validate_ipo_input(ipo)

    # Build the feature vector.  Pass through textual data if provided.
    # If a prospectus_text is supplied explicitly, use it; otherwise, fall back
    # to any text stored on the IpoInput object (prospectus_text attribute).
    text = prospectus_text if prospectus_text is not None else getattr(ipo, "prospectus_text", None)
    features = build_feature_vector(ipo, prospectus_text=text)
    # Use custom coefficients if provided, otherwise default to COEFFS_V1.
    coeffs_to_use = coeffs if coeffs is not None else COEFFS_V1
    risk = risk_score_from_features(features, coeffs_to_use)
    # The inverse of the risk score can be interpreted as an "attractiveness"
    # metric.  This concept is not described in the theoretical paper but
    # remains available for downstream applications.  Callers can disable
    # attractiveness calculation by setting include_attractiveness=False.
    attractiveness = 100.0 - risk if include_attractiveness else None

    drivers: List[RiskDriverDomain] = []
    for name, value in features.items():
        coeff = coeffs_to_use.get(name)
        if coeff is None:
            # Skip features that do not influence the active coefficient set.
            continue
        contribution = coeff * value
        drivers.append(
            RiskDriverDomain(
                name=name,
                contribution_points=round(contribution, 4),
                description=(
                    f"{name}: value {value:.2f} * weight {coeff:.2f} "
                    f"≈ {contribution:.3f} logit points"
                ),
            )
        )

    return RiskResult(
        risk_score=risk,
        attractiveness_percent=attractiveness,
        model_version=model_version if model_version is not None else MODEL_VERSION,
        drivers=drivers,
        raw_features=features,
    )
