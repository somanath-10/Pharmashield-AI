import json
import urllib.request
import urllib.error

url = "http://localhost:8000/api/cases/analyze"
payload = {
    "query": "Is there a cheaper version of Augmentin 625 Duo?",
    "brand_name": "Augmentin 625 Duo",
    "patient_context": {
        "budget_sensitive": True
    }
}

headers = {
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"Status Code: {response.getcode()}")
        print(f"Detected Intent: {result.get('intent')}")
        print(f"Overall Risk: {result.get('risk_level')}")
        print("API is fully working over HTTP!")
except urllib.error.URLError as e:
    print(f"HTTP Request failed: {e}")
