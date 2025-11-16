from ..entities import IpoInput


def _valuation_from_ps_multiple(offer_usd: float, revenue_ttm: float) -> float:
    """
    Approximate a valuation risk feature using an implicit price-to-sales multiple:

        PS_ipo = offer_value / revenue_ttm

    The mapping to [0, 1] is heuristic and should be calibrated with data:

        PS <= 1     -> low valuation risk
        PS ~ 2      -> medium valuation risk
        PS >= 4     -> high valuation risk
    """
    if revenue_ttm <= 0:
        # No or negative revenue: treat as maximum valuation risk
        return 1.0

    ps_ipo = offer_usd / revenue_ttm

    # Piecewise linear mapping; thresholds are placeholders for later calibration
    if ps_ipo <= 1.0:
        return 0.1
    elif ps_ipo <= 2.0:
        # Interpolate between 0.1 and 0.5
        return 0.1 + 0.4 * (ps_ipo - 1.0) / 1.0
    elif ps_ipo <= 4.0:
        # Interpolate between 0.5 and 1.0
        return 0.5 + 0.5 * (ps_ipo - 2.0) / 2.0
    else:
        return 1.0


def compute_valuation_feature(ipo: IpoInput) -> float:
    """
    Compute the valuation feature f_val in [0, 1] for a given IPO.
    """
    offer_mid = (ipo.deal_terms.price_low + ipo.deal_terms.price_high) / 2.0
    offer_usd = offer_mid * ipo.deal_terms.offer_shares

    return _valuation_from_ps_multiple(
        offer_usd=offer_usd,
        revenue_ttm=ipo.financials.revenue_ttm,
    )
