"""
Example: scoring an UPX-like IPO using the IPO Risk Score model.

This script builds an IpoInput instance for a micro-float IPO similar to
Uptrend Holdings Limited ("UPX") and computes its risk score.
"""

from __future__ import annotations

from ipo_risk_score.domain.risk.engine import compute_ipo_risk
from ipo_risk_score.domain.risk.entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
    RiskResult,
)


def build_upx_like_ipo() -> IpoInput:
    """
    Construct an IpoInput instance that approximates the UPX case study
    used in the paper.

    Values are illustrative and should not be treated as exact deal terms.
    """
    return IpoInput(
        ticker="UPX",
        company_name="Uptrend Holdings Limited",
        country="HK",
        sector="Construction",
        deal_terms=DealTermsDomain(
            price_low=4.0,
            price_high=5.0,
            offer_shares=1_500_000,
            free_float_pct=10.0,  # micro-float
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=8_290_827.0,
            gross_margin=30.5,
            net_margin=12.6,
            growth_yoy=43.9,
        ),
        underwriter_tier=4,  # 1 = top tier, 5 = lowest tier
        auditor_is_big4=False,  # non-Big4 auditor
        sector_cyclicality=2,  # cyclical sector
        region_risk_tier=2,  # higher-risk region
        # Example sector price-to-sales multiple (e.g. peer group PS)
        sector_ps_multiple=1.5,
    )


def print_risk_result(result: RiskResult) -> None:
    """
    Pretty-print the risk score, attractiveness, and driver breakdown.
    """
    print(f"Risk score:        {result.risk_score:.2f} / 100")
    print(f"Attractiveness:    {result.attractiveness_percent:.2f} / 100")
    print(f"Model version:     {result.model_version}")
    print("\nDrivers (normalized features × 100):")
    for driver in result.drivers:
        print(
            f"  - {driver.name:<12}: "
            f"{driver.contribution_points:6.1f} pts "
            f"({driver.description})"
        )

    print("\nRaw features:")
    for name, value in result.raw_features.items():
        print(f"  {name:<12} = {value:.4f}")


def main() -> None:
    """
    Build a UPX-like IPO, compute its risk score, and print the results.
    """
    ipo = build_upx_like_ipo()
    result = compute_ipo_risk(ipo)
    print_risk_result(result)


if __name__ == "__main__":
    main()
