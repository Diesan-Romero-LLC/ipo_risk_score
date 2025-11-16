"""
Feature computation package for IPO risk scoring.

This package exposes a single public entry point:

    build_feature_vector(ipo: IpoInput) -> Dict[str, float]

All concrete feature engineering is implemented in the internal modules
(liquidity, valuation, quality, context, ...).
"""

from .builder import build_feature_vector

__all__ = ["build_feature_vector"]
