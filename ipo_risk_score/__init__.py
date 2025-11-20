"""
IPO Risk Score package.

This package exposes the domain models and scoring engine under
`ipo_risk_score.domain`.
"""

from importlib import metadata

try:  # pragma: no cover - fallback for editable installs
    __version__ = metadata.version("ipo-risk-score")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = ["__version__"]
