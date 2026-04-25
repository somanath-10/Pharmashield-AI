import json
import urllib.request
import urllib.error

url = "http://localhost:8000/api/ingest/public"
headers = {"Content-Type": "application/json"}

print("Triggering CDSCO Public Data Ingestion...")
req = urllib.request.Request(url, data=b"{}", headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"New Records Created: {result.get('records_created')}")
        
        if result.get('status') == "ok":
            print("Successfully synchronized with CDSCO Public sources!")
except urllib.error.URLError as e:
    print(f"Ingestion Request failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
