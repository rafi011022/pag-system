# decision_layer/policy_generator.py

DISASTER_THRESHOLDS = {
    "flood": {"high": 0.8, "medium": 0.5, "low": 0.0},
    "cyclone": {"high": 0.75, "medium": 0.45, "low": 0.0},
    "drought": {"high": 0.7, "medium": 0.4, "low": 0.0},
}

STAKEHOLDER_ACTIONS = {
    "DDM": {
        "high": [
            "জেলা দুর্যোগ ব্যবস্থাপনা কমিটির জরুরি সভা আহ্বান করুন",
            "আশ্রয়কেন্দ্র প্রস্তুত করুন এবং ত্রাণ সামগ্রী বিতরণ শুরু করুন",
            "সেনাবাহিনী ও BNCC-এর সাথে সমন্বয় করুন",
            "জরুরি SMS সতর্কতা পাঠান (১৬৪০৪)"
        ],
        "medium": [
            "পরিস্থিতি পর্যবেক্ষণ বাড়ান",
            "আশ্রয়কেন্দ্র প্রস্তুত রাখুন",
            "ত্রাণ সামগ্রী মজুদ নিশ্চিত করুন"
        ],
        "low": ["নিয়মিত পর্যবেক্ষণ চালু রাখুন"]
    },
    "UNO": {
        "high": [
            "উপজেলা দুর্যোগ ব্যবস্থাপনা কমিটি সক্রিয় করুন",
            "স্থানীয় স্বেচ্ছাসেবক দল মোতায়েন করুন",
            "ইউনিয়ন পরিষদের মাধ্যমে মাইকিং শুরু করুন"
        ],
        "medium": [
            "ঝুঁকিপূর্ণ পরিবার চিহ্নিত করুন",
            "স্থানীয় স্বাস্থ্যসেবা প্রস্তুত রাখুন"
        ],
        "low": ["নিয়মিত রিপোর্ট সংগ্রহ করুন"]
    },
    "NGO": {
        "high": [
            "ত্রাণ বিতরণ কার্যক্রম শুরু করুন (শুকনো খাবার, ওষুধ, পানি পরিশোধন ট্যাবলেট)",
            "নারী ও শিশুদের জন্য বিশেষ সহায়তা নিশ্চিত করুন",
            "WASH কার্যক্রম সক্রিয় করুন"
        ],
        "medium": [
            "প্রাক-অবস্থান সহায়তা সামগ্রী প্রস্তুত করুন",
            "সম্প্রদায় স্বাস্থ্যকর্মীদের প্রস্তুত রাখুন"
        ],
        "low": ["সচেতনতামূলক কার্যক্রম পরিচালনা করুন"]
    }
}

def assess_risk(rainfall_mm, river_level_m, wind_speed_kmh, disaster_type="flood"):
    """Calculate a composite risk score (0–1)."""
    if disaster_type == "flood":
        score = (
            min(rainfall_mm / 300, 1.0) * 0.4 +
            min(river_level_m / 15, 1.0) * 0.6
        )
    elif disaster_type == "cyclone":
        score = (
            min(wind_speed_kmh / 250, 1.0) * 0.6 +
            min(rainfall_mm / 200, 1.0) * 0.4
        )
    elif disaster_type == "drought":
        score = max(0, 1 - rainfall_mm / 50) * 0.7 + 0.3
    else:
        score = 0.5
    return round(min(score, 1.0), 3)

def get_risk_level(score, disaster_type="flood"):
    thresholds = DISASTER_THRESHOLDS.get(disaster_type, DISASTER_THRESHOLDS["flood"])
    if score >= thresholds["high"]:
        return "high"
    elif score >= thresholds["medium"]:
        return "medium"
    return "low"

def calculate_impact(risk_score, region_population=500000):
    """Estimate disaster impact."""
    return {
        "estimated_affected": int(region_population * risk_score * 0.3),
        "estimated_displaced": int(region_population * risk_score * 0.1),
        "crop_damage_crore_bdt": round(risk_score * 200, 1),
        "economic_loss_crore_bdt": round(risk_score * 500, 1),
        "risk_score": risk_score
    }

def calculate_roi(anticipatory_cost_crore, risk_score, region_population=500000):
    """Calculate ROI of anticipatory action."""
    impact = calculate_impact(risk_score, region_population)
    total_loss = impact["economic_loss_crore_bdt"]
    avoided_loss = total_loss * risk_score * 0.6
    roi = ((avoided_loss - anticipatory_cost_crore) / anticipatory_cost_crore) * 100
    return {
        "anticipatory_cost_crore": anticipatory_cost_crore,
        "estimated_loss_without_action_crore": total_loss,
        "estimated_avoided_loss_crore": round(avoided_loss, 1),
        "roi_percent": round(roi, 1),
        "recommendation": "অগ্রিম পদক্ষেপ নিন" if roi > 0 else "পরিস্থিতি পর্যবেক্ষণ করুন"
    }

def generate_policy(region, disaster_type, rainfall_mm, river_level_m=5, wind_speed_kmh=20, population=500000):
    """Main policy generator function."""
    risk_score = assess_risk(rainfall_mm, river_level_m, wind_speed_kmh, disaster_type)
    risk_level = get_risk_level(risk_score, disaster_type)
    impact = calculate_impact(risk_score, population)
    roi = calculate_roi(anticipatory_cost_crore=10, risk_score=risk_score, region_population=population)

    report = {
        "region": region,
        "disaster_type": disaster_type,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "impact_assessment": impact,
        "roi_analysis": roi,
        "stakeholder_recommendations": {
            stakeholder: STAKEHOLDER_ACTIONS[stakeholder][risk_level]
            for stakeholder in STAKEHOLDER_ACTIONS
        }
    }
    return report

if __name__ == "__main__":
    import json
    report = generate_policy(
        region="সিলেট",
        disaster_type="flood",
        rainfall_mm=250,
        river_level_m=12,
        population=600000
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
