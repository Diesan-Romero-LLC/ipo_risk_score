# IPO Risk Score

This project contains a prototype implementation of the **IPO Risk Score** model, a logistic‑bounded framework for estimating the ex‑ante investment risk of initial public offerings (IPOs).  The model maps multiple normalized risk factors into a single score between 0 and 100.

## Overview

The core components of the model are:

* **Feature engineering**: deal terms, liquidity, valuation, underwriter and auditor quality, and sector/geographic context are encoded as normalized features in \([0, 1]\).
* **Linear logit**: a weighted sum of these features (plus an intercept) yields a logit \(z\).
* **Logistic transformation**: the risk score is computed as \(100/(1+e^{-z})\), ensuring the result lies in \([0, 100]\).

### Choosing logistic coefficients

By default, the model uses a set of heuristic coefficients (`COEFFS_V1`) to combine
features into a logit.  These values are reasonable placeholders when no
calibration data is available.  If you wish to more closely follow the
formulas presented in `ipo_risk_score.tex`, you can use the example
coefficient set (`COEFFS_TEX_EXAMPLE`) or supply your own coefficients:

```python
from ipo_risk_score.domain.risk import (
    compute_ipo_risk,
    COEFFS_TEX_EXAMPLE,
)

# compute risk using the example coefficients from the paper
result = compute_ipo_risk(ipo, coeffs=COEFFS_TEX_EXAMPLE, model_version="v1-tex-example")

### Usage

pip install -e .
python examples/score_upx.py
