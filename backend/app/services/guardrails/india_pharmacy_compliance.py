from app.schemas.case import CaseAnalyzeResponse

class IndiaPharmacyComplianceGuard:
    def validate(self, response: CaseAnalyzeResponse) -> CaseAnalyzeResponse:
        disclaimer = "Pharmacist review required before clinical, dispensing, substitution, or patient-specific action."
        if disclaimer not in response.action_plan:
            response.action_plan.append(disclaimer)
        return response
