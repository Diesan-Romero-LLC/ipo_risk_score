"""Pruebas para escenarios de liquidez extremos."""

from ipo_risk_score.domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from ipo_risk_score.domain.risk.features.liquidity import compute_liquidity_features


def _make_ipo(free_float_pct: float, lockup_days: int) -> IpoInput:
    return IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=10.0,
            price_high=10.0,
            offer_shares=1_000_000,
            free_float_pct=free_float_pct,
            lockup_days=lockup_days,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=10_000_000.0,
            gross_margin=30.0,
            net_margin=10.0,
            growth_yoy=20.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )


def test_micro_float_extreme_risk() -> None:
    """Un free float del 1 % y sin lock-up produce f_liq_total > 0.8."""
    ipo = _make_ipo(free_float_pct=1.0, lockup_days=0)
    feats = compute_liquidity_features(ipo)
    assert feats["f_liq_total"] > 0.8


def test_full_float_low_risk() -> None:
    """Un free float del 100 % y lock-up completo produce f_liq_total < 0.2."""
    ipo = _make_ipo(free_float_pct=100.0, lockup_days=180)
    feats = compute_liquidity_features(ipo)
    assert feats["f_liq_total"] < 0.2
