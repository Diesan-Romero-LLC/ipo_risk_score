from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DealTermsDomain:
    price_low: float
    price_high: float
    offer_shares: int
    free_float_pct: float
    lockup_days: int


@dataclass
class FinancialSnapshotDomain:
    revenue_ttm: float
    gross_margin: float
    net_margin: float
    growth_yoy: float


@dataclass
class IpoInput:
    ticker: Optional[str]
    company_name: Optional[str]
    country: Optional[str]
    sector: Optional[str]

    deal_terms: DealTermsDomain
    financials: FinancialSnapshotDomain

    underwriter_tier: int
    auditor_is_big4: bool
    sector_cyclicality: int
    region_risk_tier: int

    # New: sector price-to-sales multiple used to compute valuation premium.
    sector_ps_multiple: Optional[float] = None

    # Optional: raw text from the IPO prospectus or related documents.  If provided,
    # it will be used to compute a textual sentiment risk feature.  A value of
    # ``None`` means no textual feature will be included.  See
    # `features/textual.py` for details.
    prospectus_text: Optional[str] = None


@dataclass
class RiskDriverDomain:
    name: str
    contribution_points: float
    description: str


@dataclass
class RiskResult:
    risk_score: float
    # The attractiveness percentage is defined as 100 − risk_score.  It is kept
    # optional to allow callers of compute_ipo_risk to disable its computation
    # via the include_attractiveness flag.  If include_attractiveness=False
    # the value will be None.
    attractiveness_percent: Optional[float]
    model_version: str
    drivers: List[RiskDriverDomain]
    raw_features: Dict[str, float]
