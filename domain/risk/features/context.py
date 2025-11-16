from typing import Dict

from ..entities import IpoInput


def compute_context_features(ipo: IpoInput) -> Dict[str, float]:
    """
    Compute contextual risk features such as sector and geographic risk.

    For now we expose:
        - f_geo: combined sector/geography risk in [0, 1]

    Expected ranges:
        ipo.sector_cyclicality in {0, 1, 2}
        ipo.region_risk_tier in {0, 1, 2}
    """
    s = ipo.sector_cyclicality
    g = ipo.region_risk_tier

    f_geo_raw = (s + g) / 4.0
    f_geo = max(0.0, min(f_geo_raw, 1.0))

    return {
        "f_geo": f_geo,
    }
