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
        # No or negative revenue: treat as maximum valuation risk.
        return 1.0

    ps_ipo = offer_usd / revenue_ttm

    if ps_ipo <= 1.0:
        return 0.1
    if ps_ipo <= 2.0:
        # Interpolate between 0.1 and 0.5.
        return 0.1 + 0.4 * (ps_ipo - 1.0) / 1.0
    if ps_ipo <= 4.0:
        # Interpolate between 0.5 and 1.0.
        return 0.5 + 0.5 * (ps_ipo - 2.0) / 2.0
    return 1.0


def compute_valuation_feature(ipo: IpoInput) -> float:
    """
    Compute the valuation feature f_val in [0, 1] for a given IPO.

    If a sector price-to-sales multiple is provided (sector_ps_multiple > 0),
    compute the premium as (PS_ipo - PS_sector) / PS_sector and clamp the
    result into [0, 1], reflecting the relative valuation premium suggested in
    the theoretical model. If no valid sector multiple is provided, fall back
    to a heuristic mapping based on the price-to-sales ratio alone.
    """
    offer_mid = (ipo.deal_terms.price_low + ipo.deal_terms.price_high) / 2.0
    offer_usd = offer_mid * ipo.deal_terms.offer_shares

    revenue_ttm = ipo.financials.revenue_ttm
    # Price-to-sales multiple of the IPO
    ps_ipo = offer_usd / revenue_ttm if revenue_ttm > 0 else None

    sector_ps = ipo.sector_ps_multiple
    if sector_ps is not None and sector_ps > 0 and ps_ipo is not None:
        premium = (ps_ipo - sector_ps) / sector_ps
        # Clamp premium to [0, 1]; negative premium yields 0 (no risk premium)
        return max(0.0, min(1.0, premium))

    # Fallback: heuristic based solely on the IPO's own PS multiple
    return _valuation_from_ps_multiple(
        offer_usd=offer_usd,
        revenue_ttm=ipo.financials.revenue_ttm,
    )
