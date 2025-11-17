from typing import Dict

from ..entities import IpoInput
from .context import compute_context_features
from .financials import compute_financial_features
from .liquidity import compute_liquidity_features
from .quality import compute_quality_features
from .valuation import compute_valuation_feature


def build_feature_vector(ipo: IpoInput) -> Dict[str, float]:
    """
    Assemble all features into a flat dict with values in [0,1].
    """
    features: Dict[str, float] = {}
    features.update(compute_liquidity_features(ipo))
    features["f_val"] = compute_valuation_feature(ipo)
    features.update(compute_quality_features(ipo))
    features.update(compute_context_features(ipo))
    features.update(compute_financial_features(ipo))
    return features
