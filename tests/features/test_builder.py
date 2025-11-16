from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features import build_feature_vector


def test_feature_vector_has_expected_keys():
    ipo = IpoInput(
        ticker="BUILDER",
        company_name="Builder Test",
        country="US",
        sector="Tech",
        deal_terms=DealTermsDomain(
            price_low=6,
            price_high=6,
            offer_shares=1_000_000,
            free_float_pct=25,
            lockup_days=120,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=3_000_000,
            gross_margin=28.0,
            net_margin=11.0,
            growth_yoy=50.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
    )

    feats = build_feature_vector(ipo)

    expected_keys = {
        "f_liq",
        "f_lock",
        "f_liq_total",
        "f_val",
        "f_uw",
        "f_aud",
        "f_geo",
    }

    assert expected_keys.issubset(feats.keys())
    for v in feats.values():
        assert 0.0 <= v <= 1.0
