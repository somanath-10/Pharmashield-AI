from __future__ import annotations

from app.core.constants import PHARMACIST_REVIEW_DISCLAIMER
from app.schemas.case import CaseAnalyzeResponse
from app.services.guardrails.compliance import ComplianceGuardrail
from app.services.guardrails.medical_safety import MedicalSafetyGuardrail


class OutputValidator:
    def __init__(self) -> None:
        self.medical = MedicalSafetyGuardrail()
        self.compliance = ComplianceGuardrail()

    def validate(self, response: CaseAnalyzeResponse) -> CaseAnalyzeResponse:
        response.summary = self.medical.enforce(response.summary)
        response.action_plan = self.compliance.validate_actions(response.action_plan)
        response.draft_prescriber_message = self.medical.enforce(response.draft_prescriber_message)
        response.draft_patient_message = self.medical.enforce(response.draft_patient_message)
        response.pharmacist_review_required = True
        if PHARMACIST_REVIEW_DISCLAIMER not in response.summary:
            response.summary = f"{response.summary}\n\n{PHARMACIST_REVIEW_DISCLAIMER}"
        return response
