"""Pruebas básicas y de casos límite para la función compute_financial_features."""

from domain.risk.entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
)
from domain.risk.features.financials import compute_financial_features


def test_financial_feature_range() -> None:
    """El feature financiero siempre debe estar en [0, 1]."""
    ipo = IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=10.0,
            price_high=10.0,
            offer_shares=1_000_000,
            free_float_pct=50.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=10_000_000.0,
            gross_margin=30.0,
            net_margin=10.0,
            growth_yoy=25.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )
    f_fin = compute_financial_features(ipo)["f_fin"]
    assert 0.0 <= f_fin <= 1.0


def test_financial_feature_maximum_risk() -> None:
    """Si margen y crecimiento son negativos, f_fin debe ser 1.0."""
    ipo = IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=1.0,
            price_high=1.0,
            offer_shares=1_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=1_000_000.0,
            gross_margin=10.0,
            net_margin=-5.0,
            growth_yoy=-10.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )
    f_fin = compute_financial_features(ipo)["f_fin"]
    assert abs(f_fin - 1.0) < 1e-9


def test_financial_feature_minimum_risk() -> None:
    """Con alta rentabilidad y crecimiento, f_fin debe ser 0.0."""
    ipo = IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=1.0,
            price_high=1.0,
            offer_shares=1_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=1_000_000.0,
            gross_margin=60.0,
            net_margin=30.0,
            growth_yoy=60.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )
    f_fin = compute_financial_features(ipo)["f_fin"]
    assert abs(f_fin - 0.0) < 1e-9


def test_financial_feature_intermediate() -> None:
    """
    Con margen neto=10 y crecimiento=25 %, los riesgos parciales son 0.5 y 0.5,
    por lo que f_fin debe ser 0.5.
    """
    ipo = IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=1.0,
            price_high=1.0,
            offer_shares=1_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=1_000_000.0,
            gross_margin=30.0,
            net_margin=10.0,
            growth_yoy=25.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )
    f_fin = compute_financial_features(ipo)["f_fin"]
    assert abs(f_fin - 0.5) < 1e-9


def test_financial_feature_mixed_cases() -> None:
    """
    Si la rentabilidad es negativa pero el crecimiento es alto (o viceversa),
    f_fin es la media de los riesgos parciales: aquí -5 % de margen (riesgo 1.0)
    y 60 % de crecimiento (riesgo 0.0) -> f_fin = 0.5.
    """
    ipo = IpoInput(
        ticker=None,
        company_name=None,
        country=None,
        sector=None,
        deal_terms=DealTermsDomain(
            price_low=1.0,
            price_high=1.0,
            offer_shares=1_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=1_000_000.0,
            gross_margin=30.0,
            net_margin=-5.0,
            growth_yoy=60.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )
    f_fin = compute_financial_features(ipo)["f_fin"]
    assert abs(f_fin - 0.5) < 1e-9
