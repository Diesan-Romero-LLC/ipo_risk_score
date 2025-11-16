from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features.quality import compute_quality_features


def test_quality_features_valid_range():
    ipo = IpoInput(
        ticker="QUAL",
        company_name="Quality Test",
        country="US",
        sector="Finance",
        deal_terms=DealTermsDomain(
            price_low=4,
            price_high=4,
            offer_shares=500_000,
            free_float_pct=30,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=2_000_000,
            gross_margin=40.0,
            net_margin=15.0,
            growth_yoy=10.0,
        ),
        underwriter_tier=5,  # worst
        auditor_is_big4=False,
        sector_cyclicality=2,
        region_risk_tier=2,
    )

    feats = compute_quality_features(ipo)

    assert feats["f_uw"] == 1.0  # worst tier -> highest risk
    assert feats["f_aud"] == 1.0  # non-Big4 -> risk = 1
