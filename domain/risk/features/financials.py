"""
Financial feature engineering for the IPO Risk Score model.

This module exposes a single function, ``compute_financial_features``,
which encodes the overall financial health of a company into a normalized
risk feature.  Strong margins and high growth lower risk; weak or negative
values increase risk.
"""

from typing import Dict

from ..entities import IpoInput


def compute_financial_features(ipo: IpoInput) -> Dict[str, float]:
    """
    Compute a combined financial risk feature f_fin in [0, 1].

    Mapping (heuristic):
      - Net margin <= 0%  => risk_net = 1.0
      - Net margin >= 20% => risk_net = 0.0
      - Linear in between.
      - Growth <= 0%      => risk_growth = 1.0
      - Growth >= 50%     => risk_growth = 0.0
      - Linear in between.

    f_fin is the average of risk_net and risk_growth.
    """
    net_margin = ipo.financials.net_margin
    growth = ipo.financials.growth_yoy
    if net_margin <= 0.0:
        risk_net = 1.0
    elif net_margin >= 20.0:
        risk_net = 0.0
    else:
        risk_net = 1.0 - (net_margin / 20.0)
    if growth <= 0.0:
        risk_growth = 1.0
    elif growth >= 50.0:
        risk_growth = 0.0
    else:
        risk_growth = 1.0 - (growth / 50.0)
    f_fin = (risk_net + risk_growth) / 2.0
    f_fin = max(0.0, min(f_fin, 1.0))
    return {"f_fin": f_fin}
