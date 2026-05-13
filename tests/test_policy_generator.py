# tests/test_policy_generator.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from decision_layer.policy_generator import (
    assess_risk, get_risk_level, calculate_impact,
    calculate_roi, generate_policy, STAKEHOLDER_ACTIONS
)

class TestAssessRisk:
    def test_high_rainfall_high_risk(self):
        score = assess_risk(rainfall_mm=300, river_level_m=14, wind_speed_kmh=20, disaster_type="flood")
        assert score >= 0.7

    def test_low_rainfall_low_risk(self):
        score = assess_risk(rainfall_mm=5, river_level_m=2, wind_speed_kmh=10, disaster_type="flood")
        assert score <= 0.5

    def test_cyclone_wind_dominant(self):
        score = assess_risk(rainfall_mm=10, river_level_m=2, wind_speed_kmh=220, disaster_type="cyclone")
        assert score >= 0.5

    def test_score_capped_at_one(self):
        score = assess_risk(rainfall_mm=9999, river_level_m=999, wind_speed_kmh=9999, disaster_type="flood")
        assert score <= 1.0

    def test_score_non_negative(self):
        score = assess_risk(rainfall_mm=0, river_level_m=0, wind_speed_kmh=0, disaster_type="flood")
        assert score >= 0.0

class TestRiskLevel:
    def test_high_level(self):
        assert get_risk_level(0.9) == "high"

    def test_medium_level(self):
        assert get_risk_level(0.6) == "medium"

    def test_low_level(self):
        assert get_risk_level(0.2) == "low"

    def test_boundary_high(self):
        assert get_risk_level(0.8) == "high"

    def test_boundary_medium(self):
        assert get_risk_level(0.5) == "medium"

class TestImpact:
    def test_returns_all_keys(self):
        impact = calculate_impact(0.8)
        for key in ["estimated_affected", "estimated_displaced",
                    "crop_damage_crore_bdt", "economic_loss_crore_bdt", "risk_score"]:
            assert key in impact

    def test_higher_risk_more_affected(self):
        low  = calculate_impact(0.2)
        high = calculate_impact(0.9)
        assert high["estimated_affected"] > low["estimated_affected"]

    def test_values_non_negative(self):
        impact = calculate_impact(0.5)
        assert all(v >= 0 for v in impact.values() if isinstance(v, (int, float)))

class TestROI:
    def test_returns_all_keys(self):
        roi = calculate_roi(10, 0.8)
        for key in ["anticipatory_cost_crore", "estimated_loss_without_action_crore",
                    "estimated_avoided_loss_crore", "roi_percent", "recommendation"]:
            assert key in roi

    def test_high_risk_positive_roi(self):
        roi = calculate_roi(anticipatory_cost_crore=5, risk_score=0.9)
        assert roi["roi_percent"] > 0

    def test_recommendation_present(self):
        roi = calculate_roi(10, 0.8)
        assert roi["recommendation"] in ["অগ্রিম পদক্ষেপ নিন", "পরিস্থিতি পর্যবেক্ষণ করুন"]

class TestGeneratePolicy:
    def test_full_policy_structure(self):
        policy = generate_policy("সিলেট", "flood", rainfall_mm=250, river_level_m=12)
        assert "region" in policy
        assert "risk_score" in policy
        assert "stakeholder_recommendations" in policy
        assert set(policy["stakeholder_recommendations"].keys()) == {"DDM", "UNO", "NGO"}

    def test_high_risk_non_empty_recommendations(self):
        policy = generate_policy("কুড়িগ্রাম", "flood", rainfall_mm=300, river_level_m=15)
        for stakeholder, actions in policy["stakeholder_recommendations"].items():
            assert len(actions) > 0, f"{stakeholder} has no recommendations for high risk"

    def test_region_preserved(self):
        policy = generate_policy("ঢাকা", "cyclone", rainfall_mm=100, wind_speed_kmh=150)
        assert policy["region"] == "ঢাকা"
