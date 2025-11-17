"""
Risk scoring subpackage for the IPO Risk Score model.

This package exposes the high-level API (`compute_ipo_risk`) and domain types
used by the model.
"""

from .calibration import fit_coefficients
from .engine import compute_ipo_risk
from .entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
    RiskDriverDomain,
    RiskResult,
)
from .features.textual import compute_textual_features
from .logistic import COEFFS_TEX_EXAMPLE, COEFFS_V1, risk_score_from_features

__all__ = [
    "DealTermsDomain",
    "FinancialSnapshotDomain",
    "IpoInput",
    "RiskDriverDomain",
    "RiskResult",
    "compute_ipo_risk",
    "COEFFS_V1",
    "COEFFS_TEX_EXAMPLE",
    "risk_score_from_features",
    "fit_coefficients",
    "compute_textual_features",
]
