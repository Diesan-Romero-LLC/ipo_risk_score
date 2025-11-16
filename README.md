# IPO Risk Radar – Logistic-Bounded IPO Risk Score

Author: **Diesan Romero**  
Contact: `me@diesanromero.com`

This repository contains a **logistic-bounded risk scoring framework** for Initial Public Offerings (IPOs).  
The goal is to map multi-dimensional IPO characteristics into a **bounded risk score in [0, 100]**, where:

- `0`  → lowest ex-ante risk  
- `100` → highest ex-ante risk

The project includes:

- A **Python implementation** of the IPO Risk Score.
- A **scientific-style paper** (LaTeX) describing the model.
- Optional integration path with a **FastAPI** service.

---

## Contents

- `domain/risk` → core model (framework-agnostic, pure Python)
- `examples` → runnable examples (e.g. score an UPX-like IPO)
- `tests` → optional unit tests for the model
- `paper` → LaTeX source (and optionally PDF) of the working paper


---

## Requirements

- **Python**: 3.10+ recommended (3.9+ should work).
- For the core model (`domain/risk`) there are **no hard dependencies**.
- For development and testing, recommended packages:

```text
pytest>=7.0
pydantic>=2.0,<3.0        # only needed if you build an API / schemas
fastapi>=0.110            # optional, if you expose the model via HTTP
uvicorn[standard]>=0.23   # optional, to run FastAPI locally
```

---

## Installation

From the root of the repository:

```bash
# (optional) create and activate a virtual environment
# python -m venv .venv
# source .venv/bin/activate      # Linux / macOS
# .venv\Scriptsctivate         # Windows

# If you have a requirements file:
pip install -r ./requirements.txt

# Or install only what you need, e.g.:
pip install pytest
```

---

## Example: scoring an UPX-like IPO

You can use `examples/score_upx.py` as a reference (create it if not present):

```python
from domain.risk.entities import (
    DealTermsDomain,
    FinancialSnapshotDomain,
    IpoInput,
)
from domain.risk.engine import compute_ipo_risk


def main():
    ipo = IpoInput(
        ticker="UPX",
        company_name="Uptrend Holdings Limited",
        country="HK",
        sector="Construction",
        deal_terms=DealTermsDomain(
            price_low=4.0,
            price_high=5.0,
            offer_shares=1_500_000,
            free_float_pct=10.0,
            lockup_days=180,
        ),
        financials=FinancialSnapshotDomain(
            revenue_ttm=8_290_827.0,
            gross_margin=30.5,
            net_margin=12.6,
            growth_yoy=43.9,
        ),
        underwriter_tier=4,        # 1 = top tier, 5 = lowest tier
        auditor_is_big4=False,     # non-Big-4
        sector_cyclicality=2,      # highly cyclical
        region_risk_tier=2,        # higher-risk region
    )

    result = compute_ipo_risk(ipo)

    print(f"Risk score: {result.risk_score:.2f} / 100")
    print(f"Attractiveness: {result.attractiveness_percent:.2f} / 100")
    print("Drivers:")
    for d in result.drivers:
        print(f"  - {d.name}: {d.contribution_points} pts ({d.description})")


if __name__ == "__main__":
    main()
```

You will see:

- A risk score in `[0, 100]`.
- An attractiveness score (`100 - risk`).
- The per-driver contributions.

---

## Paper and citation

The scientific description of this model is available in:

- `docs/paper/ipo_risk_score.tex`

If you use this framework in academic or professional work, please cite:

> Diesan Romero, *A Logistic-Bounded Risk Scoring Framework for Initial Public Offerings (IPOs)*, SSRN Working Paper, 2025.
