from __future__ import annotations
from typing import Any, Dict

from app.core.constants import PHARMACIST_REVIEW_DISCLAIMER
from app.services.guardrails.compliance import ComplianceGuardrail
from app.services.guardrails.medical_safety import MedicalSafetyGuardrail

class OutputValidator:
    def __init__(self) -> None:
        self.medical = MedicalSafetyGuardrail()
        self.compliance = ComplianceGuardrail()

    def validate(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return response

def validate_role_output(role: str, result_data: Dict[str, Any]) -> Dict[str, Any]:
    # Basic implementation of role output validation
    validator = OutputValidator()
    if role == "PHARMACIST":
        if "pharmacist_review_required" not in result_data:
            result_data["pharmacist_review_required"] = PHARMACIST_REVIEW_DISCLAIMER
    return validator.validate(result_data)
