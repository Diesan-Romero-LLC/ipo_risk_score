from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features.context import compute_context_features


def test_context_feature_valid_range():
    ipo = IpoInput(
        ticker="CTX",
        company_name="Contextual Test",
        country="UK",
        sector="Energy",
        deal_terms=DealTermsDomain(
            price_low=8,
            price_high=10,
            offer_shares=2_000_000,
            free_float_pct=40,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=8_000_000,
            gross_margin=35.0,
            net_margin=18.0,
            growth_yoy=30.0,
        ),
        underwriter_tier=1,
        auditor_is_big4=True,
        sector_cyclicality=2,
        region_risk_tier=2,
    )

    feats = compute_context_features(ipo)
    assert 0.0 <= feats["f_geo"] <= 1.0
