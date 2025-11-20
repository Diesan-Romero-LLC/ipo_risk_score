from typing import Dict

from ..entities import IpoInput


def compute_quality_features(ipo: IpoInput) -> Dict[str, float]:
    """
    Compute features related to deal and reporting quality:

        - f_uw:  underwriter quality (higher => more risk)
        - f_aud: auditor quality (1 if non-Big4, 0 if Big4)
    """
    # underwriter_tier is expected in [1, 5] where 1 = best, 5 = weakest.
    f_uw_raw = (ipo.underwriter_tier - 1) / 4.0
    f_uw = max(0.0, min(f_uw_raw, 1.0))

    f_aud = 0.0 if ipo.auditor_is_big4 else 1.0

    return {
        "f_uw": f_uw,
        "f_aud": f_aud,
    }
