"""
Risk scoring subpackage for the IPO Risk Score model.

This package exposes the high-level API (`compute_ipo_risk`) and domain types
used by the model.
"""

from .engine import compute_ipo_risk
from .entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
    RiskDriverDomain,
    RiskResult,
)

__all__ = [
    "DealTermsDomain",
    "FinancialSnapshotDomain",
    "IpoInput",
    "RiskDriverDomain",
    "RiskResult",
    "compute_ipo_risk",
]
