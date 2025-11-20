import pytest

from ipo_risk_score.domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from ipo_risk_score.domain.risk.validators import ValidationError, validate_ipo_input


def _build_base_ipo() -> IpoInput:
    return IpoInput(
        ticker="BASE",
        company_name="Base IPO",
        country="US",
        sector="Tech",
        deal_terms=DealTermsDomain(
            price_low=10,
            price_high=12,
            offer_shares=1_000_000,
            free_float_pct=30.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=10_000_000,
            gross_margin=30.0,
            net_margin=10.0,
            growth_yoy=20.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
    )


def test_validation_accepts_reasonable_input():
    ipo = _build_base_ipo()
    # Should not raise.
    validate_ipo_input(ipo)


def test_validation_rejects_negative_free_float():
    ipo = _build_base_ipo()
    ipo.deal_terms.free_float_pct = -5.0

    with pytest.raises(ValidationError):
        validate_ipo_input(ipo)


def test_validation_rejects_unrealistic_price():
    ipo = _build_base_ipo()
    ipo.deal_terms.price_high = 50_000.0

    with pytest.raises(ValidationError):
        validate_ipo_input(ipo)


def test_validation_rejects_unrealistic_revenue():
    ipo = _build_base_ipo()
    ipo.financials.revenue_ttm = 2_000_000_000_000.0  # 2 trillion

    with pytest.raises(ValidationError):
        validate_ipo_input(ipo)


def test_validation_rejects_bad_ticker_pattern():
    ipo = _build_base_ipo()
    ipo.ticker = "BAD TICKER"  # contains space

    with pytest.raises(ValidationError):
        validate_ipo_input(ipo)


def test_validation_rejects_ticker_with_control_char():
    ipo = _build_base_ipo()
    ipo.ticker = "BAD\n"  # newline

    with pytest.raises(ValidationError):
        validate_ipo_input(ipo)
