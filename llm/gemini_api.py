# llm/gemini_api.py
import requests

GEMINI_API_KEY = "your_gemini_api_key"  # Replace with your API key
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_gemini_alert(risk_level, region, disaster_type):
    params = {"key": GEMINI_API_KEY}
    prompt = f"""
    তুমি একজন বাংলাদেশের দুর্যোগ ব্যবস্থাপনা বিশেষজ্ঞ।
    নিচের তথ্যের ভিত্তিতে সাধারণ মানুষের জন্য সহজ বাংলায় একটি সংক্ষিপ্ত সতর্কতা বার্তা তৈরি করো (সর্বোচ্চ ২ বাক্য):
    - ঝুঁকির মাত্রা: {risk_level}
    - অঞ্চল: {region}
    - দুর্যোগের ধরন: {disaster_type}
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, params=params, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    alert = generate_gemini_alert("উচ্চ", "সিলেট", "বন্যা")
    print(f"Gemini Alert: {alert}")
