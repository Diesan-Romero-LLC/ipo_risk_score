```
# IPO Risk Score

This project contains a prototype implementation of the **IPO Risk Score** model, a logistic-bounded framework for estimating the ex-ante investment risk of initial public offerings (IPOs). The model maps multiple normalized risk factors into a single score between 0 and 100.

The reference model and notation are described in the LaTeX document `ipo_risk_score.tex` (not included here). This repository aims to mirror that formulation as closely as possible while remaining flexible and extensible.

---

## Overview

The core components of the model are:

- **Feature engineering**
  Deal terms, liquidity, valuation, underwriter and auditor quality, sector/geographic context, **financial strength** (profitability/growth), and **textual sentiment** (prospectus tone) are encoded as normalized features in \([0, 1]\).

- **Linear logit**
  A weighted sum of these features (plus an intercept) yields a logit \(z\):
  \[
    z = b_0 + \sum_i b_i f_i
  \]

- **Logistic transformation**
  The risk score is computed as:
  \[
    \text{RiskScore} = \frac{100}{1 + e^{-z}}
  \]
  ensuring the result lies in \([0, 100]\).

The high-level API is `compute_ipo_risk`, which takes an `IpoInput` and returns a `RiskResult` containing:

- `risk_score` -- risk in \([0, 100]\)
- `attractiveness_percent` -- optional, defined as \(100 - \text{risk_score}\)
- `model_version` -- version tag for the model used
- `drivers` -- per-feature contributions (for explainability)
- `raw_features` -- the underlying normalized features

---

## Model Inputs

The main input type is:

```python
from ipo_risk_score.domain.risk.entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
)

```

-   `DealTermsDomain`

    -   `price_low`, `price_high`

    -   `offer_shares`

    -   `free_float_pct`

    -   `lockup_days`

-   `FinancialSnapshotDomain`

    -   `revenue_ttm`

    -   `gross_margin`

    -   `net_margin`

    -   `growth_yoy`

-   `IpoInput`

    -   `ticker`, `company_name`

    -   `country`, `sector`

    -   `deal_terms: DealTermsDomain`

    -   `financials: FinancialSnapshotDomain`

    -   `underwriter_tier` (1 = top tier, higher = lower quality)

    -   `auditor_is_big4` (bool)

    -   `sector_cyclicality` (e.g. 1 = non-cyclical, 2 = cyclical)

    -   `region_risk_tier` (e.g. 1 = low risk, 2 = higher risk)

    -   `sector_ps_multiple` (optional sector price-to-sales multiple)

    -   `prospectus_text` (optional raw text string for sentiment)

* * * * *

Logistic Coefficients
---------------------

The logistic model coefficients live in `domain/risk/logistic.py`.

Two main sets are exposed:

-   `COEFFS_V1` -- heuristic default coefficients, good as a starting point when there is no calibration data.

-   `COEFFS_TEX_EXAMPLE` -- example coefficients aligned with the formulas and relative weights discussed in `ipo_risk_score.tex`.

Each is a dictionary with keys:

-   `"intercept"` -- scalar bias

-   `"f_liq_total"` -- liquidity + lock-up combined risk

-   `"f_val"` -- valuation premium risk

-   `"f_uw"` -- underwriter tier risk

-   `"f_aud"` -- auditor quality risk

-   `"f_geo"` -- sector/geography risk

-   `"f_fin"` -- financial robustness risk (optional extension)

-   `"f_text"` -- textual sentiment risk (optional extension)

You can choose the coefficient set at scoring time:

```
from ipo_risk_score.domain.risk import (
    compute_ipo_risk,
    COEFFS_V1,
    COEFFS_TEX_EXAMPLE,
)

# With default heuristic coefficients
result_default = compute_ipo_risk(ipo)

# With example coefficients from the paper
result_tex = compute_ipo_risk(
    ipo,
    coeffs=COEFFS_TEX_EXAMPLE,
    model_version="v1-tex-example",
)

```

* * * * *

Liquidity Feature
-----------------

The liquidity feature follows the paper's structure:

-   `f_liq` -- free float and dollar-value-of-float driven risk

-   `f_lock` -- lock-up driven risk

-   `f_liq_total` -- weighted combination of `f_liq` and `f_lock`

Implementation lives in `domain/risk/features/liquidity.py` and uses configurable parameters:

-   `alpha_free_float` (default 0.7)

-   `alpha_dollar_float` (default 0.3)

-   `lockup_max_days` (default 180)

-   `weight_liquidity` (default 0.7)

-   `weight_lockup` (default 0.3)

These can be overridden if you call `compute_liquidity_features` directly, or by adjusting defaults in the file.

At the high level, `compute_ipo_risk` will use the defaults to compute `f_liq_total` as described in the LaTeX document.

* * * * *

Valuation Feature
-----------------

The valuation feature `f_val` compares the IPO's implied price-to-sales multiple with a sector multiple (if available):

-   If `sector_ps_multiple` is provided, a relative premium is computed according to the paper (e.g. IPO PS / sector PS).

-   If not provided, a fallback heuristic is used.

Implementation lives in `domain/risk/features/valuation.py` and is wired into the feature builder.

* * * * *

Quality Features (Underwriter & Auditor)
----------------------------------------

The paper assigns risk based on:

-   **Underwriter tier** -- top tier underwriters lower perceived risk.

-   **Auditor type** -- Big4 vs non-Big4.

These are encoded as:

-   `f_uw`

-   `f_aud`

in `domain/risk/features/quality.py`.

Both are normalized into ([0, 1]) with higher values representing higher risk (lower quality).

* * * * *

Context Features (Sector & Region)
----------------------------------

Sector and geographic risk factors are represented via:

-   `sector_cyclicality`

-   `region_risk_tier`

and mapped into a single feature `f_geo` in `domain/risk/features/context.py`.

The mapping mirrors the qualitative descriptions in the paper (e.g. cyclical sectors/higher-risk regions get higher `f_geo`).

* * * * *

Financial Feature (f_fin)
-------------------------

The financial feature encodes profitability and growth:

-   **Inputs**: `net_margin`, `growth_yoy`

-   **Heuristic mapping** (can be tuned):

    -   Net margin:

        -   `<= 0%` → high risk

        -   `>= 20%` → low risk

    -   Growth:

        -   `<= 0%` → high risk

        -   `>= 50%` → low risk

-   `f_fin` is the average of the margin-risk and growth-risk components, clamped to ([0, 1]).

Implementation: `domain/risk/features/financials.py`.

This feature is an extension beyond the core paper but is conceptually consistent (financial weakness increases risk). You can disable or modify it by:

-   Removing `"f_fin"` from your coefficient dictionary, or

-   Editing `financials.py` to match your calibration.

* * * * *

Textual Sentiment Feature (f_text)
----------------------------------

If you have access to the IPO prospectus or related descriptive text, you can incorporate a simple textual sentiment feature:

Implementation: `domain/risk/features/textual.py`.

### Input options

1.  **Attach text to the IPO object**:

    ```py
    from ipo_risk_score.domain.risk.entities import IpoInput

    ipo = IpoInput(
        ticker="XYZ",
        company_name="Example Corp",
        country="US",
        sector="Tech",
        # ...
        sector_ps_multiple=3.0,
        prospectus_text=open("prospectus.txt").read(),
    )

    result = compute_ipo_risk(ipo)

    ```

2.  **Override text at scoring time**:

    ```
    result = compute_ipo_risk(
        ipo,
        prospectus_text="Our company expects strong growth and profit opportunities...",
    )

    ```

If a `prospectus_text` keyword argument is supplied, it overrides the text stored on the `IpoInput`. Otherwise, the scorer uses the `prospectus_text` attribute if present.

### How it works

The default implementation uses a small lexicon of positive/negative words and converts the sentiment into a normalized feature:

-   More negative words → higher `f_text`

-   More positive words → lower `f_text`

-   Neutral/no text → `f_text ≈ 0.5`

You can modify or completely replace this logic in `textual.py` (e.g. using a real NLP model).

* * * * *

Calibration
-----------

To align the coefficients with actual historical data (as discussed in the paper), you can use the calibration helper:

```py
from ipo_risk_score.domain.risk import fit_coefficients
from ipo_risk_score.domain.risk import compute_ipo_risk

# ipos: Sequence[IpoInput]
# targets: Sequence[int] (0/1 risk outcomes, ex post)
coeffs = fit_coefficients(ipos, targets)

result = compute_ipo_risk(
    ipo,
    coeffs=coeffs,
    model_version="v1-calibrated",
)

```

The function:

-   Builds feature vectors using the same pipeline as `compute_ipo_risk`.

-   Fits a `sklearn.linear_model.LogisticRegression`.

-   Returns a coefficient dict compatible with `risk_score_from_features`.

This matches the calibration procedure described in the LaTeX document.

> Note: You must have `scikit-learn` and `numpy` installed for calibration:
>
> ```bash
> pip install scikit-learn numpy
>
> ```

* * * * *

High-Level API
--------------

The main entry point is:

```py
from ipo_risk_score.domain.risk import (
    IpoInput,
    DealTermsDomain,
    FinancialSnapshotDomain,
    compute_ipo_risk,
)

```

Basic usage:

```py
ipo = IpoInput(
    ticker="XYZ",
    company_name="Example Corp",
    country="US",
    sector="Tech",
    deal_terms=DealTermsDomain(
        price_low=10.0,
        price_high=12.0,
        offer_shares=5_000_000,
        free_float_pct=25.0,
        lockup_days=180,
    ),
    financials=FinancialSnapshotDomain(
        revenue_ttm=50_000_000.0,
        gross_margin=45.0,
        net_margin=12.0,
        growth_yoy=30.0,
    ),
    underwriter_tier=2,
    auditor_is_big4=True,
    sector_cyclicality=1,
    region_risk_tier=1,
    sector_ps_multiple=4.0,
    prospectus_text=None,
)

result = compute_ipo_risk(ipo)
print(result.risk_score, result.attractiveness_percent, result.model_version)

```

You can also inspect the drivers:

```py
for driver in result.drivers:
    print(driver.name, driver.contribution_points, driver.description)

```

* * * * *

Example Script (UPX-like IPO)
-----------------------------

The repository includes an example in `examples/score_upx.py` that builds an IPO similar to **Uptrend Holdings Limited (UPX)** and scores it:

```bash
python examples/score_upx.py

```

This script:

-   Instantiates an `IpoInput` with UPX-like terms.

-   Optionally uses `prospectus_text`.

-   Computes risk with both:

    -   `COEFFS_V1` (default heuristic set)

    -   `COEFFS_TEX_EXAMPLE` (paper-inspired set)

-   Prints the risk score, attractiveness, and detailed driver breakdown.

* * * * *

Installation & Development
--------------------------

Install in editable mode:

```bash
pip install -e .

```

Then you can run the example:

```bash
python examples/score_upx.py

```

If you want to run your own experiments or integrate this into a research pipeline, import the package and use the `compute_ipo_risk` and `fit_coefficients` functions directly as shown above.

* * * * *

Notes and Limitations
---------------------

-   The financial (`f_fin`) and textual (`f_text`) features are extensions beyond the minimal specification of the original paper but follow its spirit.

-   Default coefficients are heuristic and **should be calibrated** for production use.

-   The textual sentiment feature is deliberately simple and can be replaced with more sophisticated NLP models as needed.

-   This codebase is intended for research and educational purposes and should not be used as-is as an investment recommendation system.
