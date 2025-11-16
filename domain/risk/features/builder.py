from typing import Dict

from ..entities import IpoInput
from .liquidity import compute_liquidity_features
from .valuation import compute_valuation_feature
from .quality import compute_quality_features
from .context import compute_context_features


def build_feature_vector(ipo: IpoInput) -> Dict[str, float]:
    """
    Public entry point to construct the feature vector used by the risk model.

    All features are designed to lie in [0, 1] where:
        0 = lowest risk contribution
        1 = highest risk contribution

    The returned dictionary is intentionally flat and uses stable keys
    ("f_liq_total", "f_val", "f_uw", "f_aud", "f_geo", ...), so that
    model code (e.g. logistic regression) only depends on the keys, not
    on internal implementation details.
    """
    features: Dict[str, float] = {}

    # Liquidity-related features (includes f_liq_total)
    features.update(compute_liquidity_features(ipo))

    # Valuation
    features["f_val"] = compute_valuation_feature(ipo)

    # Deal/reporting quality
    features.update(compute_quality_features(ipo))

    # Sector / geographic context
    features.update(compute_context_features(ipo))

    return features
