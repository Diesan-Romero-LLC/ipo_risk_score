from typing import Dict
from .entities import IpoInput

def build_feature_vector(ipo: IpoInput) -> Dict[str, float]:
    # Liquidez
    float_risk = 1.0 - min(ipo.deal_terms.free_float_pct / 100.0, 1.0)

    offer_mid = (ipo.deal_terms.price_low + ipo.deal_terms.price_high) / 2.0
    offer_usd = offer_mid * ipo.deal_terms.offer_shares

    if offer_usd < 10_000_000:
        size_risk = 1.0
    elif offer_usd < 100_000_000:
        size_risk = 0.5
    else:
        size_risk = 0.0

    f_liq_total = min(1.0, 0.7 * float_risk + 0.3 * size_risk)

    # TODO: valuation real
    f_val = 0.5

    f_uw = (ipo.underwriter_tier - 1) / 4.0
    f_aud = 0.0 if ipo.auditor_is_big4 else 1.0

    s = ipo.sector_cyclicality
    g = ipo.region_risk_tier
    f_geo = (s + g) / 4.0

    return {
        "f_liq_total": f_liq_total,
        "f_val": f_val,
        "f_uw": f_uw,
        "f_aud": f_aud,
        "f_geo": f_geo,
    }