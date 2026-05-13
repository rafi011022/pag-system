# llm/claude_api.py
import requests

CLAUDE_API_KEY = "your_claude_api_key"  # Replace with your API key
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

def generate_claude_alert(risk_level, region, disaster_type):
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    prompt = f"""
    তুমি একজন বাংলাদেশের দুর্যোগ ব্যবস্থাপনা বিশেষজ্ঞ।
    নিচের তথ্যের ভিত্তিতে সাধারণ মানুষের জন্য সহজ বাংলায় একটি সংক্ষিপ্ত সতর্কতা বার্তা তৈরি করো (সর্বোচ্চ ২ বাক্য):
    - ঝুঁকির মাত্রা: {risk_level}
    - অঞ্চল: {region}
    - দুর্যোগের ধরন: {disaster_type}
    """
    payload = {
        "model": "claude-opus-4-20250514",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    alert = generate_claude_alert("উচ্চ", "সিলেট", "বন্যা")
    print(f"Claude Alert: {alert}")
