from dataclasses import dataclass
from typing import Optional, Dict, List

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

@dataclass
class RiskDriverDomain:
    name: str
    contribution_points: float
    description: str

@dataclass
class RiskResult:
    risk_score: float
    attractiveness_percent: float
    model_version: str
    drivers: List[RiskDriverDomain]
    raw_features: Dict[str, float]