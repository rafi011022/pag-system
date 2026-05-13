# llm/mistral_api.py
import requests

MISTRAL_API_KEY = "your_mistral_api_key"  # Replace with your API key
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def generate_mistral_alert(risk_level, region, disaster_type):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
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
        "model": "mistral-large-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    alert = generate_mistral_alert("উচ্চ", "সিলেট", "বন্যা")
    print(f"Mistral Alert: {alert}")
