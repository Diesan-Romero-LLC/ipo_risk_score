import math
import re

from .entities import DealTermsDomain, FinancialSnapshotDomain, IpoInput


class ValidationError(ValueError):
    """Raised when an IPO input does not satisfy domain constraints."""

    pass


# ---------------------------------------------------------------------------
# Global security / sanity constraints
# ---------------------------------------------------------------------------

# String length constraints
MAX_TICKER_LENGTH = 16
MAX_COMPANY_NAME_LENGTH = 256
MAX_COUNTRY_LENGTH = 64
MAX_SECTOR_LENGTH = 128

# Numeric soft bounds (domain-informed, not hard financial rules)
MAX_PRICE = 10_000.0
MAX_OFFER_SHARES = 10_000_000_000  # 10 billion
MAX_REVENUE = 1_000_000_000_000.0  # 1 trillion

# Allowed ticker pattern: uppercase letters, numbers, dot, dash
TICKER_PATTERN = re.compile(r"^[A-Z0-9.\-]+$")


def _ensure_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValidationError(f"{name} must be a finite number, got {value!r}")


def _reject_control_chars(label: str, value: str) -> None:
    """Reject strings with control characters (line breaks, tabs, etc.)."""
    for ch in value:
        if ord(ch) < 32:  # control characters range
            raise ValidationError(f"{label} contains control characters, which are not allowed")


# ---------------------------------------------------------------------------
# String / identity validation
# ---------------------------------------------------------------------------


def _validate_identity_strings(ipo: IpoInput) -> None:
    if ipo.ticker:
        if len(ipo.ticker) > MAX_TICKER_LENGTH:
            raise ValidationError(f"ticker is too long (>{MAX_TICKER_LENGTH} characters)")
        if not TICKER_PATTERN.match(ipo.ticker):
            raise ValidationError("ticker contains invalid characters; only [A-Z0-9.-] are allowed")
        _reject_control_chars("ticker", ipo.ticker)

    if ipo.company_name:
        if len(ipo.company_name) > MAX_COMPANY_NAME_LENGTH:
            raise ValidationError(
                f"company_name is too long (>{MAX_COMPANY_NAME_LENGTH} characters)"
            )
        _reject_control_chars("company_name", ipo.company_name)

    if ipo.country:
        if len(ipo.country) > MAX_COUNTRY_LENGTH:
            raise ValidationError(f"country is too long (>{MAX_COUNTRY_LENGTH} characters)")
        _reject_control_chars("country", ipo.country)

    if ipo.sector:
        if len(ipo.sector) > MAX_SECTOR_LENGTH:
            raise ValidationError(f"sector is too long (>{MAX_SECTOR_LENGTH} characters)")
        _reject_control_chars("sector", ipo.sector)


# ---------------------------------------------------------------------------
# Deal terms / financials validation
# ---------------------------------------------------------------------------


def _validate_deal_terms(deal: DealTermsDomain) -> None:
    if deal.price_low <= 0 or deal.price_high <= 0:
        raise ValidationError("price_low and price_high must be > 0")

    if deal.price_high < deal.price_low:
        raise ValidationError("price_high must be >= price_low")

    if deal.price_low > MAX_PRICE or deal.price_high > MAX_PRICE:
        raise ValidationError(f"price_low/price_high look unrealistic (> {MAX_PRICE})")

    if deal.offer_shares <= 0:
        raise ValidationError("offer_shares must be > 0")

    if deal.offer_shares > MAX_OFFER_SHARES:
        raise ValidationError(f"offer_shares looks unrealistic (> {MAX_OFFER_SHARES})")

    if not (0.0 <= deal.free_float_pct <= 100.0):
        raise ValidationError("free_float_pct must be in [0, 100]")

    if deal.lockup_days < 0:
        raise ValidationError("lockup_days must be >= 0")

    for name, value in [
        ("price_low", deal.price_low),
        ("price_high", deal.price_high),
        ("free_float_pct", deal.free_float_pct),
    ]:
        _ensure_finite(name, value)


def _validate_financials(fin: FinancialSnapshotDomain) -> None:
    if fin.revenue_ttm < 0:
        raise ValidationError("revenue_ttm must be >= 0")

    if fin.revenue_ttm > MAX_REVENUE:
        raise ValidationError(f"revenue_ttm looks unrealistic (> {MAX_REVENUE})")

    for name, value in [
        ("revenue_ttm", fin.revenue_ttm),
        ("gross_margin", fin.gross_margin),
        ("net_margin", fin.net_margin),
        ("growth_yoy", fin.growth_yoy),
    ]:
        _ensure_finite(name, value)

    # Optional soft bounds for margins and growth.
    if not (-100.0 <= fin.gross_margin <= 100.0):
        raise ValidationError("gross_margin looks out of bounds (-100, 100)")

    if not (-100.0 <= fin.net_margin <= 100.0):
        raise ValidationError("net_margin looks out of bounds (-100, 100)")

    if not (-100.0 <= fin.growth_yoy <= 300.0):
        raise ValidationError("growth_yoy looks out of bounds (-100, 300)")


def _validate_categorical(ipo: IpoInput) -> None:
    if not (1 <= ipo.underwriter_tier <= 5):
        raise ValidationError("underwriter_tier must be in [1, 5]")

    if ipo.sector_cyclicality not in (0, 1, 2):
        raise ValidationError("sector_cyclicality must be in {0, 1, 2}")

    if ipo.region_risk_tier not in (0, 1, 2):
        raise ValidationError("region_risk_tier must be in {0, 1, 2}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_ipo_input(ipo: IpoInput) -> None:
    """
    Validate that an IpoInput instance satisfies basic domain and security constraints.

    This function is intentionally strict: it is designed to protect the model
    from obviously-invalid, malicious, or absurd inputs (NaNs, infinities, huge
    values, or suspicious strings).
    """
    _validate_identity_strings(ipo)
    _validate_deal_terms(ipo.deal_terms)
    _validate_financials(ipo.financials)
    _validate_categorical(ipo)
