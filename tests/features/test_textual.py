"""Pruebas para el feature de sentimiento textual."""

from domain.risk.entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput
from domain.risk.features.textual import compute_textual_features


def _dummy_ipo() -> IpoInput:
    return IpoInput(
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
            growth_yoy=20.0,
        ),
        underwriter_tier=3,
        auditor_is_big4=True,
        sector_cyclicality=1,
        region_risk_tier=1,
        sector_ps_multiple=2.0,
    )


def test_textual_feature_neutral() -> None:
    """Sin texto, f_text debe ser 0.5."""
    ipo = _dummy_ipo()
    feats = compute_textual_features(ipo, None)
    assert abs(feats["f_text"] - 0.5) < 1e-9


def test_textual_feature_positive_sentiment() -> None:
    """Texto con palabras positivas debe bajar f_text por debajo de 0.5."""
    ipo = _dummy_ipo()
    text = "Nuestro strong growth y robust profit outlook indican expansión y opportunity."
    feats = compute_textual_features(ipo, text)
    assert feats["f_text"] < 0.5


def test_textual_feature_negative_sentiment() -> None:
    """Texto con palabras negativas debe subir f_text por encima de 0.5."""
    ipo = _dummy_ipo()
    text = "Volatile markets y uncertain competition pueden conducir a decline y loss."
    feats = compute_textual_features(ipo, text)
    assert feats["f_text"] > 0.5
