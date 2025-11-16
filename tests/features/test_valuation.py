from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features.valuation import compute_valuation_feature


def test_valuation_reasonable_range():
    ipo = IpoInput(
        ticker="VAL",
        company_name="Valuation Test",
        country="US",
        sector="Tech",
        deal_terms=DealTermsDomain(
            price_low=5,
            price_high=5,
            offer_shares=1_000_000,
            free_float_pct=50,
            lockup_days=90,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=5_000_000,
            gross_margin=25.0,
            net_margin=10.0,
            growth_yoy=20.0,
        ),
        underwriter_tier=2,
        auditor_is_big4=False,
        sector_cyclicality=1,
        region_risk_tier=1,
    )

    val = compute_valuation_feature(ipo)
    assert 0.0 <= val <= 1.0
