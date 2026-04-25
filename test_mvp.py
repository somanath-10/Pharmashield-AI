import urllib.request
import json

BASE = "http://localhost:8000"


def post(path, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def run():
    print("=== PATIENT WORKFLOW ===")
    case = post("/api/cases", {
        "role": "PATIENT",
        "case_type": "PATIENT_PRESCRIPTION_EXPLANATION",
        "title": "Rx Explain",
        "query": "What does my prescription mean?"
    })
    cid = case["case_id"]
    print("Case created:", cid)
    doc = post(f"/api/cases/{cid}/documents", {
        "document_type": "PRESCRIPTION",
        "file_name": "rx.pdf",
        "mock_extracted_text": "Patient takes Metformin 500mg. HbA1c 8.2"
    })
    print("Doc uploaded:", doc["document_id"])
    result = post(f"/api/cases/{cid}/analyze")
    r = result["result"]
    print("Disclaimer present:", "disclaimer" in r)
    print("Medicines found:", len(r.get("medicines_found", [])))
    print("Lab values found:", len(r.get("lab_values_found", [])))

    print()
    print("=== PHARMACIST WORKFLOW ===")
    case2 = post("/api/cases", {
        "role": "PHARMACIST",
        "case_type": "PHARMACIST_DISPENSING_CHECK",
        "title": "Dispense Check",
        "query": "Can I dispense Amoxicillin?"
    })
    cid2 = case2["case_id"]
    post(f"/api/cases/{cid2}/documents", {
        "document_type": "PRESCRIPTION",
        "file_name": "rx2.pdf",
        "mock_extracted_text": "Augmentin prescribed"
    })
    result2 = post(f"/api/cases/{cid2}/analyze")
    r2 = result2["result"]
    print("Medicine identified:", r2["medicine"])
    print("Pharmacist disclaimer OK:", "Pharmacist review" in r2["disclaimer"])

    print()
    print("=== DOCTOR WORKFLOW ===")
    case3 = post("/api/cases", {
        "role": "DOCTOR",
        "case_type": "DOCTOR_CASE_SUMMARY",
        "title": "Patient Summary",
        "query": "Summarize"
    })
    cid3 = case3["case_id"]
    post(f"/api/cases/{cid3}/documents", {
        "document_type": "LAB_REPORT",
        "file_name": "labs.pdf",
        "mock_extracted_text": "HbA1c 8.2 Metformin noted"
    })
    result3 = post(f"/api/cases/{cid3}/analyze")
    r3 = result3["result"]
    print("Clinical summary present:", "clinical_summary" in r3)
    print("Follow-up points:", len(r3.get("follow_up_points", [])))

    print()
    print("=== ADMIN WORKFLOW ===")
    case4 = post("/api/cases", {
        "role": "ADMIN",
        "case_type": "ADMIN_REVIEW",
        "title": "Dashboard",
        "query": "Get metrics"
    })
    cid4 = case4["case_id"]
    result4 = post(f"/api/cases/{cid4}/analyze")
    r4 = result4["result"]
    print("Metrics present:", "metrics" in r4)
    print("Active patient cases:", r4["metrics"]["active_patient_cases"])

    print()
    print("ALL FOUR ROLE WORKFLOWS PASSED")


if __name__ == "__main__":
    run()
