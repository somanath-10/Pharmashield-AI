"""
Exhaustive Phase 3 End-to-End Test Suite
Tests every route, role, agent, ingest, intelligence, edge case, and combination.
"""
import httpx
import asyncio
import json

BASE = "http://localhost:8000"
RESULTS = []


def log(name, status, detail=""):
    icon = "[PASS]" if status else "[FAIL]"
    RESULTS.append((name, status, detail))
    print(f"{icon} {name}" + (f" | {detail}" if detail else ""))


def check(name, r, expected_keys=None, expected_status=200, detail_key=None):
    ok = r.status_code == expected_status
    data = None
    try:
        data = r.json()
    except Exception:
        data = {}
    if ok and expected_keys:
        for k in expected_keys:
            if k not in data:
                ok = False
                log(name, False, f"missing key: {k}")
                return data
    detail = ""
    if detail_key and data:
        detail = f"{detail_key}={data.get(detail_key, '')}"
    log(name, ok, detail or (r.text[:100] if not ok else ""))
    return data if ok else {}


async def main():
    async with httpx.AsyncClient(timeout=30) as c:

        # ──────────────────────────────────────────────────────
        # 1. HEALTH
        # ──────────────────────────────────────────────────────
        print("\n════ 1. HEALTH ════")
        r = await c.get(f"{BASE}/health")
        check("GET /health", r)

        # ──────────────────────────────────────────────────────
        # 2. AUTH — all 4 roles
        # ──────────────────────────────────────────────────────
        print("\n════ 2. AUTH ════")
        tokens = {}
        for role_email in ["patient@demo.com", "pharmacist@demo.com", "doctor@demo.com", "admin@demo.com"]:
            r = await c.post(f"{BASE}/auth/login", data={"username": role_email, "password": "demo123"})
            d = check(f"POST /auth/login ({role_email})", r, ["access_token", "token_type"])
            if d:
                tokens[role_email] = d["access_token"]

        # Re-login with existing user (idempotent)
        r = await c.post(f"{BASE}/auth/login", data={"username": "patient@demo.com", "password": "demo123"})
        check("POST /auth/login (re-login existing user)", r, ["access_token"])

        admin_headers = {}
        if tokens.get("admin@demo.com"):
            admin_headers = {"Authorization": f"Bearer {tokens['admin@demo.com']}"}

        # ──────────────────────────────────────────────────────
        # 3. CASE CREATION — all roles + all case_types
        # ──────────────────────────────────────────────────────
        print("\n════ 3. CASE CREATION ════")
        case_ids = {}

        combos = [
            ("PATIENT",     "PATIENT_PRESCRIPTION_EXPLANATION", "Augmentin Rx for patient",
             "Explain my Augmentin 625 prescription. Is there a cheaper option? Can I use Ayushman card?"),
            ("PATIENT",     "PATIENT_REPORT_EXPLANATION",       "Lab report patient",
             "My HbA1c is 8.2. What does it mean? Is Metformin appropriate?"),
            ("PHARMACIST",  "PHARMACIST_DISPENSING_CHECK",      "Augmentin dispensing check",
             "Augmentin 625 not available. Patient wants cheaper option. WhatsApp seller found. Prescription available."),
            ("PHARMACIST",  "PHARMACIST_SUBSTITUTION_CHECK",    "Substitution request",
             "Patient asks to substitute Augmentin 625 with a generic. Is this allowed?"),
            ("DOCTOR",      "DOCTOR_CASE_SUMMARY",              "Patient case summary",
             "Summarize the patient prescription, lab report, and affordability concern."),
            ("ADMIN",       "ADMIN_REVIEW",                     "Admin weekly analytics",
             "Show all high risk cases this week including NSQ matches and online seller risk."),
        ]

        for role, ctype, title, query in combos:
            r = await c.post(f"{BASE}/api/cases", json={
                "role": role, "case_type": ctype, "title": title, "query": query
            }, headers=admin_headers)
            d = check(f"POST /api/cases ({role}/{ctype})", r, ["case_id", "role", "status"])
            if d:
                case_ids[f"{role}_{ctype}"] = d["case_id"]

        # LIST + GET
        r = await c.get(f"{BASE}/api/cases", headers=admin_headers)
        check("GET /api/cases (list all)", r)

        if not case_ids:
            log("Case creation prerequisite", False, "No case IDs created; cannot continue test suite")
            print("\n" + "=" * 60)
            passed = [x for x in RESULTS if x[1]]
            failed = [x for x in RESULTS if not x[1]]
            print(f"TOTAL: {len(RESULTS)} | PASS: {len(passed)} | FAIL: {len(failed)}")
            return

        first_id = list(case_ids.values())[0]
        r = await c.get(f"{BASE}/api/cases/{first_id}", headers=admin_headers)
        check("GET /api/cases/{id} (valid)", r, ["case_id"])

        r = await c.get(f"{BASE}/api/cases/nonexistent-id-xyz", headers=admin_headers)
        check("GET /api/cases/{id} (invalid → 404)", r, expected_status=404)

        # ──────────────────────────────────────────────────────
        # 4. DOCUMENT UPLOAD (multipart with dummy PDF text)
        # ──────────────────────────────────────────────────────
        print("\n════ 4. DOCUMENT UPLOAD ════")
        pid = case_ids.get("PATIENT_PATIENT_PRESCRIPTION_EXPLANATION")
        if pid:
            dummy_pdf = b"%PDF-1.4 Augmentin 625mg tablet. Take twice daily after food. Dr. Sharma, Reg No. 12345"
            r = await c.post(
                f"{BASE}/api/cases/{pid}/documents",
                files={"file": ("prescription.pdf", dummy_pdf, "application/pdf")},
                headers=admin_headers
            )
            check("POST /cases/{id}/documents (PDF upload)", r)

        # ──────────────────────────────────────────────────────
        # 5. DOCUMENT SEARCH
        # ──────────────────────────────────────────────────────
        print("\n════ 5. DOCUMENT SEARCH ════")
        if pid:
            r = await c.post(f"{BASE}/api/cases/{pid}/search",
                             json={"query": "Augmentin cheaper alternative generic Jan Aushadhi", "role": "PATIENT"},
                             headers=admin_headers)
            check("POST /cases/{id}/search (PATIENT)", r)

        phid = case_ids.get("PHARMACIST_PHARMACIST_DISPENSING_CHECK")
        if phid:
            r = await c.post(f"{BASE}/api/cases/{phid}/search",
                             json={"query": "Schedule H1 prescription batch NSQ check", "role": "PHARMACIST"},
                             headers=admin_headers)
            check("POST /cases/{id}/search (PHARMACIST)", r)

        # ──────────────────────────────────────────────────────
        # 6. CASE ANALYZE — every role, every context combo
        # ──────────────────────────────────────────────────────
        print("\n════ 6. CASE ANALYSIS ════")

        analyze_cases = [
            # (label, case_key, question, context, expected_agents_partial, expected_risk)
            ("PATIENT basic explanation",
             "PATIENT_PATIENT_PRESCRIPTION_EXPLANATION",
             "Explain my prescription",
             {"drug_name": "Augmentin 625"},
             ["prescription_compliance_agent"], None),

            ("PATIENT budget + scheme",
             "PATIENT_PATIENT_PRESCRIPTION_EXPLANATION",
             "Is there a cheaper option? Can I use Ayushman card?",
             {"drug_name": "Augmentin 625", "budget_sensitive": True,
              "scheme_name": "PM-JAY", "purchase_context": "retail_pharmacy"},
             ["price_janaushadhi_agent", "scheme_claim_agent"], "MEDIUM"),

            ("PATIENT lab report HbA1c",
             "PATIENT_PATIENT_REPORT_EXPLANATION",
             "What does HbA1c 8.2 mean? Any cheaper medicine?",
             {"drug_name": "Metformin", "budget_sensitive": True},
             ["price_janaushadhi_agent"], None),

            ("PHARMACIST full check: stock+NSQ+WhatsApp+price",
             "PHARMACIST_PHARMACIST_DISPENSING_CHECK",
             "Can I dispense? Check NSQ, WhatsApp seller, and stock",
             {"drug_name": "Augmentin 625", "composition": "Amoxicillin + Clavulanic Acid",
              "quantity_on_hand": 0, "budget_sensitive": True, "prescription_available": True,
              "seller_type": "whatsapp_seller", "claim_text": "generic ozempic no prescription needed",
              "manufacturer": "Example Pharma Ltd", "batch_number": "PCT2026A"},
             ["price_janaushadhi_agent", "nsq_spurious_agent", "online_seller_risk_agent",
              "inventory_batch_agent"], "CRITICAL"),

            ("PHARMACIST no prescription + Schedule H1",
             "PHARMACIST_PHARMACIST_SUBSTITUTION_CHECK",
             "Patient wants to buy without prescription",
             {"drug_name": "Augmentin 625", "prescription_available": False},
             ["prescription_compliance_agent"], "HIGH"),

            ("PHARMACIST MRP exceeds NPPA ceiling",
             "PHARMACIST_PHARMACIST_DISPENSING_CHECK",
             "Is MRP correct for Augmentin 625?",
             {"drug_name": "Augmentin 625", "mrp": 250.0, "budget_sensitive": True},
             ["price_janaushadhi_agent"], "HIGH"),

            ("PHARMACIST out of stock only",
             "PHARMACIST_PHARMACIST_DISPENSING_CHECK",
             "Is Augmentin in stock?",
             {"drug_name": "Augmentin 625", "quantity_on_hand": 0, "location_id": "HYD_STORE_001"},
             ["inventory_batch_agent"], None),

            ("DOCTOR case summary with affordability",
             "DOCTOR_DOCTOR_CASE_SUMMARY",
             "Summarize the patient case and affordability concern",
             {"drug_name": "Augmentin 625", "budget_sensitive": True},
             ["price_janaushadhi_agent"], None),

            ("DOCTOR case summary no context",
             "DOCTOR_DOCTOR_CASE_SUMMARY",
             "Summarize the uploaded patient documents",
             {},
             [], None),

            ("ADMIN live analytics",
             "ADMIN_ADMIN_REVIEW",
             "Show analytics",
             {},
             [], None),
        ]

        for label, case_key, question, ctx, expected_agents, expected_risk in analyze_cases:
            cid = case_ids.get(case_key)
            if not cid:
                log(f"POST /analyze ({label})", False, f"no case_id for {case_key}")
                continue
            payload = {}
            if question:
                payload["question"] = question
            if ctx:
                payload["context"] = ctx
            r = await c.post(f"{BASE}/api/cases/{cid}/analyze", json=payload, headers=admin_headers)
            d = check(f"POST /analyze ({label})", r, ["case_id", "risk_level", "agents_run"])
            if d:
                agents = d.get("agents_run", [])
                risk = d.get("risk_level", "")
                missing_agents = [a for a in expected_agents if a not in agents]
                if missing_agents:
                    log(f"  ↳ agents check ({label})", False, f"missing: {missing_agents}")
                else:
                    log(f"  ↳ agents check ({label})", True, f"agents={agents}")
                if expected_risk and risk != expected_risk:
                    log(f"  ↳ risk check ({label})", False, f"expected {expected_risk}, got {risk}")
                else:
                    log(f"  ↳ risk check ({label})", True, f"risk={risk}")

        # Edge case: analyze with invalid case_id
        r = await c.post(f"{BASE}/api/cases/bad-id-xyz/analyze", json={}, headers=admin_headers)
        check("POST /analyze (invalid case_id → 404)", r, expected_status=404)

        # ──────────────────────────────────────────────────────
        # 7. INTELLIGENCE CHECKS — all 7 endpoints, multiple inputs
        # ──────────────────────────────────────────────────────
        print("\n════ 7. INTELLIGENCE CHECKS ════")

        intel_tests = [
            # (endpoint, label, payload, expected_risk)
            ("price-check", "Augmentin budget HIGH",
             {"drug_name": "Augmentin 625", "mrp": 200, "patient_budget_sensitive": True}, "HIGH"),
            ("price-check", "Metformin budget LOW",
             {"drug_name": "Metformin", "mrp": 45, "patient_budget_sensitive": True}, "LOW"),
            ("price-check", "Unknown drug",
             {"drug_name": "SomeDrugXYZ", "patient_budget_sensitive": False}, "LOW"),

            ("janaushadhi-search", "Amoxicillin search",
             {"drug_name": "Amoxicillin", "patient_budget_sensitive": True}, None),
            ("janaushadhi-search", "Unknown drug search",
             {"drug_name": "SomeDrugXYZ", "patient_budget_sensitive": True}, None),

            ("nsq-check", "CRITICAL exact batch+mfr",
             {"drug_name": "Paracetamol", "manufacturer": "Example Pharma Ltd",
              "batch_number": "PCT2026A"}, "CRITICAL"),
            ("nsq-check", "MEDIUM missing batch",
             {"drug_name": "Paracetamol"}, "MEDIUM"),
            ("nsq-check", "LOW no match — but no batch so still MEDIUM",
             {"drug_name": "Aspirin"}, "MEDIUM"),

            ("schedule-check", "H1 no Rx → HIGH",
             {"medicine_name": "Augmentin 625", "prescription_available": False}, "HIGH"),
            ("schedule-check", "H1 with Rx → MEDIUM",
             {"medicine_name": "Augmentin 625", "prescription_available": True}, "MEDIUM"),
            ("schedule-check", "Suspicious claim → HIGH",
             {"medicine_name": "Augmentin 625", "prescription_available": True,
              "claim_text": "no prescription needed"}, "HIGH"),
            ("schedule-check", "Unknown drug",
             {"medicine_name": "SomeDrugXYZ", "prescription_available": True}, None),

            ("scheme-check", "PM-JAY retail → not covered",
             {"scheme_name": "PM-JAY", "hospitalized": False, "purchase_context": "retail_pharmacy"}, "LOW"),
            ("scheme-check", "PM-JAY hospitalized",
             {"scheme_name": "PM-JAY", "hospitalized": True, "purchase_context": "hospital"}, "LOW"),
            ("scheme-check", "No scheme name",
             {"hospitalized": False, "purchase_context": "retail_pharmacy"}, "LOW"),

            ("seller-risk-check", "WhatsApp + no Rx → HIGH",
             {"seller_type": "whatsapp_seller", "claim_text": "generic Ozempic without prescription"}, "HIGH"),
            ("seller-risk-check", "Instagram + no license → HIGH",
             {"seller_type": "instagram_seller", "claim_text": "no bill no mrp"}, "HIGH"),
            ("seller-risk-check", "Licensed distributor → LOW",
             {"seller_name": "Good Supplier", "seller_type": "licensed_distributor",
              "license_number": "DL-99999", "batch_number": "B001"}, "LOW"),

            ("inventory-check", "HYD_STORE_001 out of stock",
             {"drug_name": "Augmentin 625", "quantity_on_hand": 0,
              "location_id": "HYD_STORE_001"}, "MEDIUM"),
            ("inventory-check", "Unknown drug",
             {"drug_name": "SomeDrugXYZ", "quantity_on_hand": 10}, None),
        ]

        for endpoint, label, payload, expected_risk in intel_tests:
            r = await c.post(f"{BASE}/api/intelligence/{endpoint}", json=payload, headers=admin_headers)
            d = check(f"POST /intelligence/{endpoint} ({label})", r)
            if d and expected_risk:
                got = d.get("risk_level", "")
                if got != expected_risk:
                    log(f"  ↳ risk ({label})", False, f"expected {expected_risk}, got {got}")
                else:
                    log(f"  ↳ risk ({label})", True, f"risk={got}")

        # ──────────────────────────────────────────────────────
        # 8. INGEST ENDPOINTS — all 6
        # ──────────────────────────────────────────────────────
        print("\n════ 8. INGEST ════")

        r = await c.post(f"{BASE}/api/ingest/cdsco-nsq", json={
            "drug_name": "TestDrug", "brand_name": "TestBrand",
            "manufacturer": "TestMfr", "batch_number": "TEST-B001",
            "failure_reason": "Dissolution test failed", "alert_type": "NSQ", "source": "CDSCO"
        }, headers=admin_headers)
        check("POST /ingest/cdsco-nsq", r, ["id"])

        r = await c.post(f"{BASE}/api/ingest/nppa-prices", json={
            "brand_name": "TestBrand", "generic_name": "TestGeneric",
            "composition": "TestComp 500mg", "mrp": 120.0,
            "ceiling_price": 90.0, "source": "NPPA"
        }, headers=admin_headers)
        check("POST /ingest/nppa-prices", r, ["id"])

        r = await c.post(f"{BASE}/api/ingest/janaushadhi-products", json={
            "generic_name": "TestGeneric", "composition": "TestComp 500mg",
            "strength": "500mg", "dosage_form": "Tablet",
            "janaushadhi_price": 35.0, "availability_status": "AVAILABLE", "source": "PMBJP"
        }, headers=admin_headers)
        check("POST /ingest/janaushadhi-products", r, ["id"])

        r = await c.post(f"{BASE}/api/ingest/schedule-rules", json={
            "drug_name": "TestDrug", "composition": "TestComp",
            "schedule_category": "H", "requires_prescription": True,
            "requires_sales_register": True, "rule_summary": "Prescription required, maintain register.",
            "source": "CDSCO"
        }, headers=admin_headers)
        check("POST /ingest/schedule-rules", r, ["id"])

        r = await c.post(f"{BASE}/api/ingest/scheme-rules", json={
            "scheme_name": "Corporate OPD", "scheme_type": "Corporate",
            "eligibility_summary": "Employees of empanelled corporations",
            "coverage_summary": "OPD reimbursement up to Rs 15000/year",
            "applies_to_retail_pharmacy": True,
            "applies_to_hospitalization": False,
            "source": "Employer"
        }, headers=admin_headers)
        check("POST /ingest/scheme-rules", r, ["id"])

        r = await c.post(f"{BASE}/api/ingest/suppliers", json={
            "supplier_name": "Trusted Pharma Dist",
            "seller_type": "licensed_distributor",
            "license_number": "DL-77777", "state": "Karnataka",
            "verification_status": "VERIFIED", "risk_score": 0.1,
            "risk_reasons": []
        }, headers=admin_headers)
        check("POST /ingest/suppliers", r, ["id"])

        # Verify just-ingested NSQ shows in check
        r = await c.post(f"{BASE}/api/intelligence/nsq-check", json={
            "drug_name": "TestDrug", "manufacturer": "TestMfr", "batch_number": "TEST-B001"
        }, headers=admin_headers)
        d = check("POST /intelligence/nsq-check (just-ingested batch)", r)
        if d:
            log("  ↳ ingested NSQ picked up", d.get("risk_level") in ("CRITICAL", "MEDIUM"),
                f"risk={d.get('risk_level')} alerts={d.get('alerts_found')}")

        # Verify just-ingested price shows
        r = await c.post(f"{BASE}/api/intelligence/price-check", json={
            "drug_name": "TestBrand", "mrp": 200.0, "patient_budget_sensitive": True
        }, headers=admin_headers)
        d = check("POST /intelligence/price-check (just-ingested price, MRP>ceiling)", r)
        if d:
            log("  ↳ MRP violation detected", d.get("risk_level") == "HIGH",
                f"risk={d.get('risk_level')}")

        # ──────────────────────────────────────────────────────
        # 9. FEEDBACK — submit, verify
        # ──────────────────────────────────────────────────────
        print("\n════ 9. FEEDBACK ════")
        for case_key in list(case_ids.keys())[:3]:
            cid = case_ids[case_key]
            r = await c.post(f"{BASE}/api/cases/{cid}/feedback", json={
                "rating": 5,
                "feedback_text": f"Workflow test for {case_key} — accurate and safe response"
            }, headers=admin_headers)
            check(f"POST /cases/{cid[:8]}.../feedback ({case_key})", r, ["feedback_id", "status"])

        # Feedback with correction
        if pid:
            r = await c.post(f"{BASE}/api/cases/{pid}/feedback", json={
                "rating": 3,
                "feedback_text": "Good but missed the Jan Aushadhi option",
                "correction_text": "Should mention PM-JAY does not cover retail OPD"
            }, headers=admin_headers)
            check("POST /cases/feedback (with correction_text)", r, ["feedback_id"])

        # Feedback on non-existent case
        r = await c.post(f"{BASE}/api/cases/bad-case-id/feedback", json={
            "rating": 5, "feedback_text": "Test"
        }, headers=admin_headers)
        check("POST /cases/feedback (invalid case → 404)", r, expected_status=404)

        # ──────────────────────────────────────────────────────
        # 10. ADMIN ANALYTICS
        # ──────────────────────────────────────────────────────
        print("\n════ 10. ADMIN ANALYTICS ════")
        r = await c.get(f"{BASE}/api/admin/analytics", headers=admin_headers)
        d = check("GET /api/admin/analytics", r, [
            "total_cases", "high_risk_cases", "nsq_matches",
            "online_seller_risk_cases", "prescription_compliance_warnings",
            "affordability_requests", "recent_audit_logs"
        ])
        if d:
            print(f"  total_cases={d.get('total_cases')} | high={d.get('high_risk_cases')} | "
                  f"nsq={d.get('nsq_matches')} | seller_risk={d.get('online_seller_risk_cases')} | "
                  f"compliance={d.get('prescription_compliance_warnings')} | "
                  f"affordability={d.get('affordability_requests')}")
            print(f"  audit_log_entries={len(d.get('recent_audit_logs', []))}")
            print(f"  avg_feedback={d.get('average_feedback_rating')}")

        r = await c.get(f"{BASE}/api/admin/audit-logs?limit=10", headers=admin_headers)
        d = check("GET /api/admin/audit-logs", r, ["count", "logs"])
        if d:
            print(f"  audit logs returned: {d.get('count')}")

        # ──────────────────────────────────────────────────────
        # SUMMARY
        # ──────────────────────────────────────────────────────
        print("\n" + "=" * 60)
        passed = [x for x in RESULTS if x[1]]
        failed = [x for x in RESULTS if not x[1]]
        print(f"TOTAL: {len(RESULTS)} | PASS: {len(passed)} | FAIL: {len(failed)}")
        if failed:
            print("\nFAILED TESTS:")
            for name, _, detail in failed:
                print(f"  [FAIL] {name} | {detail}")
        else:
            print("\nALL TESTS PASSED!")


asyncio.run(main())
