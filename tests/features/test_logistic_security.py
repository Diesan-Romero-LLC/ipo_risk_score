import math

import pytest

from domain.risk.logistic import (
    COEFFS_V1,
    FEATURE_MAX_SAFE,
    risk_score_from_features,
)


def test_risk_score_rejects_non_finite_feature():
    features = {
        "f_liq_total": math.inf,
    }

    with pytest.raises(ValueError):
        risk_score_from_features(features, COEFFS_V1)


def test_risk_score_rejects_out_of_range_feature():
    features = {
        "f_liq_total": FEATURE_MAX_SAFE + 10.0,
    }

    with pytest.raises(ValueError):
        risk_score_from_features(features, COEFFS_V1)


def test_risk_score_accepts_normal_feature_vector():
    features = {
        "f_liq_total": 0.5,
        "f_val": 0.2,
        "f_uw": 0.3,
        "f_aud": 0.0,
        "f_geo": 0.4,
    }

    score = risk_score_from_features(features, COEFFS_V1)
    assert 0.0 <= score <= 100.0
