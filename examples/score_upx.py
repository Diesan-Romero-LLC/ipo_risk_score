from domain.risk.entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
)
from domain.risk.engine import compute_ipo_risk


def main():
    ipo = IpoInput(
        ticker="UPX",
        company_name="Uptrend Holdings Limited",
        country="HK",
        sector="Construction",
        deal_terms=DealTermsDomain(
            price_low=4.0,
            price_high=5.0,
            offer_shares=1_500_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=8_290_827.0,
            gross_margin=30.5,
            net_margin=12.6,
            growth_yoy=43.9,
        ),
        underwriter_tier=4,
        auditor_is_big4=False,
        sector_cyclicality=2,
        region_risk_tier=2,
    )

    result = compute_ipo_risk(ipo)

    print(f"Risk score: {result.risk_score:.2f} / 100")
    print(f"Attractiveness: {result.attractiveness_percent:.2f} / 100")
    print("Drivers:")
    for d in result.drivers:
        print(f"  - {d.name}: {d.contribution_points} pts ({d.description})")


if __name__ == "__main__":
    main()