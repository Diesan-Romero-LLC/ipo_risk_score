import math
from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features.liquidity import compute_liquidity_features


def test_liquidity_basic_values():
    ipo = IpoInput(
        ticker="TEST",
        company_name="Example",
        country="US",
        sector="Tech",
        deal_terms=DealTermsDomain(
            price_low=10,
            price_high=12,
            offer_shares=1_000_000,
            free_float_pct=20,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=10_000_000,
            gross_margin=30.0,
            net_margin=12.0,
            growth_yoy=40.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
    )

    feats = compute_liquidity_features(ipo)

    assert 0.0 <= feats["f_liq"] <= 1.0
    assert 0.0 <= feats["f_lock"] <= 1.0
    assert 0.0 <= feats["f_liq_total"] <= 1.0
