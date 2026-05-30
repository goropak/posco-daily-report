import requests

url = "https://docs.google.com/spreadsheets/d/1hTSEWptRpjBf9Q-EJU2tl6HRgtubuVSuwd6iGwEn9Rk/export?format=csv"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    with open("fetched_data.csv", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print("Successfully fetched CSV and saved to fetched_data.csv")
    print("Preview of the content:")
    print("\n".join(response.text.splitlines()[:5]))
except Exception as e:
    print(f"Error fetching CSV: {e}")
