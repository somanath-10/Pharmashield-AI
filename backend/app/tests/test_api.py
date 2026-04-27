from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    """Test the basic health endpoint to ensure the API runs."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_doctor_dashboard_unauthorized():
    """Test that RBAC protects doctor endpoints from unauthenticated users."""
    response = client.get("/api/doctor/dashboard")
    assert response.status_code == 401

def test_pharmacist_queue_unauthorized():
    """Test that RBAC protects pharmacist endpoints."""
    response = client.get("/api/pharmacist/review-queue")
    assert response.status_code == 401

def test_patient_dashboard_unauthorized():
    """Test that RBAC protects patient endpoints."""
    response = client.get("/api/patient/dashboard")
    assert response.status_code == 401

def test_admin_analytics_unauthorized():
    """Test that RBAC protects admin endpoints."""
    response = client.get("/api/admin/analytics")
    assert response.status_code == 401

def test_admin_risk_queues_unauthorized():
    """Test that RBAC protects admin risk-queues endpoint."""
    response = client.get("/api/admin/risk-queues")
    assert response.status_code == 401

def test_admin_data_sources_unauthorized():
    """Test that RBAC protects admin data-sources endpoint."""
    response = client.get("/api/admin/data-sources")
    assert response.status_code == 401
