"""
Calibration utilities for the IPO Risk Score model.

This module provides functions to fit logistic coefficients from data.

The coefficients defined in ``logistic.py`` are heuristic placeholders.  To
make the model more data‑driven, you can collect historical IPO examples
along with a binary or continuous target representing realised risk (for
example, whether the stock traded below its offer price within a year) and
use logistic regression to estimate optimal feature weights.

``fit_coefficients`` illustrates this process.  It expects a list of
``IpoInput`` objects and corresponding target labels.  It builds the
feature vectors using the existing feature engineering pipeline and
trains a scikit‑learn ``LogisticRegression`` model.  The learned
coefficients can then be plugged into the risk scoring function.

Note: This is a simple example; depending on your data you may need to
customise the target definition, handle class imbalance or regularise the
model.  Ensure scikit‑learn is installed (``pip install scikit-learn``).
"""

from typing import Dict, Iterable, List, Sequence

from .entities import IpoInput
from .features import build_feature_vector


def fit_coefficients(
    ipos: Sequence[IpoInput],
    targets: Sequence[int],
    *,
    feature_keys: Iterable[str] = None,
    penalty: str = "l2",
    C: float = 1.0,
    solver: str = "lbfgs",
) -> Dict[str, float]:
    """
    Fit logistic regression coefficients from a dataset of IPOs.

    Parameters
    ----------
    ipos:
        A sequence of ``IpoInput`` objects representing the training
        observations.
    targets:
        A sequence of integers (0 or 1) indicating the realised outcome
        associated with each IPO.  For example, 1 could indicate that
        the IPO was deemed high risk ex‑post (underperformed) and 0
        otherwise.
    feature_keys:
        An optional iterable specifying which feature keys to include.  If
        ``None``, all features returned by ``build_feature_vector`` will be
        used.
    penalty, C, solver:
        Hyperparameters passed through to ``sklearn.linear_model.LogisticRegression``.

    Returns
    -------
    Dict[str, float]
        A dictionary mapping feature keys to the learned coefficient
        values.  The intercept is stored under the key ``"intercept"``.

    Examples
    --------
    >>> from ipo_risk_score.domain.risk.calibration import fit_coefficients
    >>> coeffs = fit_coefficients(ipos, targets)
    >>> # Use the learned coefficients
    >>> result = compute_ipo_risk(ipo, coeffs=coeffs, model_version="v1-trained")
    """
    try:
        import numpy as np  # type: ignore
        from sklearn.linear_model import LogisticRegression  # type: ignore
    except ImportError as exc:
        # To avoid excessively long lines (flake8 E501), split the error message
        # across multiple string literals. This conveys the same information
        # while keeping each line under the 100 character limit enforced by
        # our linter. We retain the guidance on how to install the required
        # dependencies for clarity.
        raise ImportError(
            "fit_coefficients requires scikit-learn and numpy. "
            "Install them via `pip install scikit-learn numpy`."
        ) from exc

    # Build feature matrix
    feature_matrix: List[List[float]] = []
    feature_names: List[str] = []
    for ipo in ipos:
        features = build_feature_vector(ipo)
        # Determine feature order on first pass
        if not feature_names:
            feature_names = list(features.keys()) if feature_keys is None else list(feature_keys)
        # Append row in order of feature_names
        feature_matrix.append([float(features.get(k, 0.0)) for k in feature_names])

    X = np.array(feature_matrix)
    y = np.array(targets, dtype=int)

    model = LogisticRegression(penalty=penalty, C=C, solver=solver, max_iter=1000)
    model.fit(X, y)

    coeffs: Dict[str, float] = {"intercept": float(model.intercept_[0])}
    for name, coef in zip(feature_names, model.coef_[0]):
        coeffs[name] = float(coef)

    return coeffs
