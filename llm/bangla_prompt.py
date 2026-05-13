# llm/bangla_prompt.py
from mistral_api import generate_mistral_alert
from claude_api import generate_claude_alert
from gemini_api import generate_gemini_alert

def generate_bangla_alert(risk_level, region, disaster_type, provider="mistral"):
    """
    Universal wrapper for generating Bangla disaster alerts.
    
    Args:
        risk_level: str - e.g. "উচ্চ", "মধ্যম", "নিম্ন"
        region: str - e.g. "সিলেট", "ঢাকা"
        disaster_type: str - e.g. "বন্যা", "ঘূর্ণিঝড়"
        provider: str - "mistral", "claude", or "gemini"
    """
    if provider == "mistral":
        return generate_mistral_alert(risk_level, region, disaster_type)
    elif provider == "claude":
        return generate_claude_alert(risk_level, region, disaster_type)
    elif provider == "gemini":
        return generate_gemini_alert(risk_level, region, disaster_type)
    else:
        return "Invalid provider. Use 'mistral', 'claude', or 'gemini'."

if __name__ == "__main__":
    for provider in ["mistral", "claude", "gemini"]:
        print(f"\n--- {provider.upper()} ---")
        alert = generate_bangla_alert("উচ্চ", "সিলেট", "বন্যা", provider=provider)
        print(alert)
