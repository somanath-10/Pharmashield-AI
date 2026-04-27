"""
PharmaShield-AI Backend Test Suite

Tests are split into:
- Unit tests (no DB, always run):  RBAC guards, health, route existence
- Integration tests (require MongoDB — marked @pytest.mark.integration):
  Auth flow, pharmacist workflow, doctor workflow, cross-role RBAC

Run unit tests only (CI mode):
  pytest app/tests

Run with MongoDB (full suite):
  MONGO_URI=<uri> pytest app/tests -m integration
"""
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ─── Skip marker for DB-dependent tests ───────────────────────────────────────
skip_if_no_db = pytest.mark.skipif(
    not os.getenv("MONGO_URI", ""),
    reason="Integration test — requires MONGO_URI environment variable"
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _register_and_login(email: str, role: str, password: str = "Secure@123") -> str:
    """Register (idempotent) then login; return Bearer token."""
    client.post("/auth/register", json={
        "name": email.split("@")[0],
        "email": email,
        "password": password,
        "role": role,
    })
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["access_token"]

# ═════════════════════════════════════════════════════════════════════════════
# UNIT TESTS — Always run, no DB required
# ═════════════════════════════════════════════════════════════════════════════

def test_health_check():
    """Liveness probe."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"

# ─── RBAC Guard Tests (401 without token) ─────────────────────────────────────

def test_doctor_dashboard_unauthorized():
    assert client.get("/api/doctor/dashboard").status_code == 401

def test_pharmacist_queue_unauthorized():
    assert client.get("/api/pharmacist/review-queue").status_code == 401

def test_patient_dashboard_unauthorized():
    assert client.get("/api/patient/dashboard").status_code == 401

def test_admin_analytics_unauthorized():
    assert client.get("/api/admin/analytics").status_code == 401

def test_admin_risk_queues_unauthorized():
    assert client.get("/api/admin/risk-queues").status_code == 401

def test_admin_data_sources_unauthorized():
    assert client.get("/api/admin/data-sources").status_code == 401

def test_pharmacist_dispensing_statuses_unauthorized():
    assert client.get("/api/pharmacist/dispensing-statuses").status_code == 401

def test_doctor_messages_unauthorized():
    assert client.get("/api/doctor/messages").status_code == 401

def test_doctor_substitution_decision_unauthorized():
    assert client.post("/api/doctor/substitution-decision", json={}).status_code == 401

def test_cases_list_unauthorized():
    assert client.get("/api/cases").status_code == 401

def test_cases_create_unauthorized():
    assert client.post("/api/cases", json={}).status_code == 401

def test_admin_audit_logs_unauthorized():
    assert client.get("/api/admin/audit-logs").status_code == 401

def test_admin_model_quality_unauthorized():
    assert client.get("/api/admin/model-quality").status_code == 401

def test_doctor_adr_reviews_unauthorized():
    assert client.get("/api/doctor/adr-reviews").status_code == 401

def test_doctor_prescription_verification_unauthorized():
    assert client.post("/api/doctor/prescription-verification", json={}).status_code == 401

def test_pharmacist_batch_check_unauthorized():
    assert client.post("/api/pharmacist/batch-check", json={}).status_code == 401

def test_pharmacist_price_check_unauthorized():
    assert client.post("/api/pharmacist/price-check", json={}).status_code == 401

def test_pharmacist_adr_draft_unauthorized():
    assert client.post("/api/pharmacist/adr-draft", json={}).status_code == 401

def test_pharmacist_dispensing_decision_unauthorized():
    assert client.post("/api/pharmacist/dispensing-decision", json={}).status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — Skipped unless MONGO_URI is set
# ═════════════════════════════════════════════════════════════════════════════

# ─── Auth ────────────────────────────────────────────────────────────────────

@skip_if_no_db
@pytest.mark.integration
def test_register_and_login_patient():
    """Full auth round-trip for PATIENT."""
    token = _register_and_login("patient_test@pharmashield.in", "PATIENT")
    assert len(token) > 20

@skip_if_no_db
@pytest.mark.integration
def test_register_duplicate_email_fails():
    email = "dup_test@pharmashield.in"
    client.post("/auth/register", json={"name": "dup", "email": email, "password": "Test@123", "role": "PATIENT"})
    resp = client.post("/auth/register", json={"name": "dup2", "email": email, "password": "Test@123", "role": "PATIENT"})
    assert resp.status_code == 400

@skip_if_no_db
@pytest.mark.integration
def test_login_wrong_password_fails():
    _register_and_login("wrongpw@pharmashield.in", "PATIENT", "RightPass@1")
    resp = client.post(
        "/auth/login",
        data={"username": "wrongpw@pharmashield.in", "password": "WrongPass@99"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401

# ─── Pharmacist Workflow ──────────────────────────────────────────────────────

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_dispensing_statuses():
    token = _register_and_login("pharm_wf@pharmashield.in", "PHARMACIST")
    resp = client.get("/api/pharmacist/dispensing-statuses", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    statuses = [s["status"] for s in resp.json()]
    assert "CAN_DISPENSE" in statuses
    assert "DO_NOT_DISPENSE" in statuses
    assert "QUARANTINE_BATCH" in statuses
    assert "NEEDS_DOCTOR_CLARIFICATION" in statuses

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_batch_check_clean():
    token = _register_and_login("pharm_batch@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/pharmacist/batch-check",
        json={"case_id": "tc-001", "medicine_name": "Paracetamol", "batch_number": "PCT2026A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_quarantined"] is False
    assert resp.json()["risk_level"] == "LOW"

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_batch_check_spurious():
    token = _register_and_login("pharm_batch2@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/pharmacist/batch-check",
        json={"case_id": "tc-002", "medicine_name": "Paracetamol", "batch_number": "FAKE2026X"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_quarantined"] is True
    assert resp.json()["risk_level"] == "HIGH"

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_price_check_overcharged():
    token = _register_and_login("pharm_price@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/pharmacist/price-check",
        json={"case_id": "tc-003", "medicine_name": "Azithromycin", "mrp": 150.0, "charged_price": 200.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_overcharged"] is True

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_dispensing_decision_invalid_status():
    token = _register_and_login("pharm_dd@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/pharmacist/dispensing-decision",
        json={"case_id": "tc-004", "medicine_name": "Aspirin", "dispensing_status": "INVALID_STATUS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_dispensing_decision_valid():
    token = _register_and_login("pharm_dd2@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/pharmacist/dispensing-decision",
        json={"case_id": "tc-005", "medicine_name": "Paracetamol", "dispensing_status": "CAN_DISPENSE"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CAN_DISPENSE"

# ─── Doctor Workflow ──────────────────────────────────────────────────────────

@skip_if_no_db
@pytest.mark.integration
def test_doctor_dashboard_authenticated():
    token = _register_and_login("doc_dash@pharmashield.in", "DOCTOR")
    resp = client.get("/api/doctor/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "adr_reviews_pending" in resp.json()
    assert "pharmacist_questions" in resp.json()

@skip_if_no_db
@pytest.mark.integration
def test_doctor_patients_returns_list():
    token = _register_and_login("doc_patients@pharmashield.in", "DOCTOR")
    resp = client.get("/api/doctor/patients", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@skip_if_no_db
@pytest.mark.integration
def test_doctor_prescription_verification_saves():
    token = _register_and_login("doc_rx@pharmashield.in", "DOCTOR")
    resp = client.post("/api/doctor/prescription-verification",
        json={"patient_name": "Test Patient", "medicines": ["Metformin 500mg"], "notes": "Refill"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "verification_id" in data
    assert data["status"] == "ACTIVE"
    assert data["expires_at"] is not None

@skip_if_no_db
@pytest.mark.integration
def test_doctor_substitution_decision_approved():
    token = _register_and_login("doc_sub@pharmashield.in", "DOCTOR")
    resp = client.post("/api/doctor/substitution-decision",
        json={
            "case_id": "tc-sub-001",
            "prescribed_medicine": "Atorvastatin 10mg",
            "proposed_substitution": "Rosuvastatin 10mg",
            "decision": "APPROVED",
            "reason": "Equivalent statin",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"

@skip_if_no_db
@pytest.mark.integration
def test_doctor_substitution_decision_invalid_action():
    token = _register_and_login("doc_sub2@pharmashield.in", "DOCTOR")
    resp = client.post("/api/doctor/substitution-decision",
        json={"case_id": "x", "prescribed_medicine": "A", "proposed_substitution": "B",
              "decision": "MAYBE", "reason": "test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400

# ─── Cross-Role RBAC ─────────────────────────────────────────────────────────

@skip_if_no_db
@pytest.mark.integration
def test_patient_cannot_access_admin():
    token = _register_and_login("patient_rbac@pharmashield.in", "PATIENT")
    resp = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403

@skip_if_no_db
@pytest.mark.integration
def test_pharmacist_cannot_call_doctor_substitution():
    token = _register_and_login("pharm_rbac@pharmashield.in", "PHARMACIST")
    resp = client.post("/api/doctor/substitution-decision",
        json={"case_id": "x", "prescribed_medicine": "A", "proposed_substitution": "B",
              "decision": "APPROVED", "reason": "test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
