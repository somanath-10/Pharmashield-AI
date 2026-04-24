from __future__ import annotations

from datetime import date
from typing import Any

from app.core.constants import normalize_drug_name


class MockPayerPolicyConnector:
    def policies(self) -> list[dict[str, Any]]:
        return [
            {
                "payer_name": "Demo Health Plan",
                "therapy_area": "GLP-1",
                "drug_name": "Wegovy",
                "policy_title": "Demo Health Plan Wegovy Coverage Policy",
                "criteria_text": (
                    "Approval criteria: diagnosis of obesity or overweight with comorbidity; "
                    "BMI documentation; prior lifestyle intervention documentation; previous therapy history where applicable; "
                    "prescriber chart notes. Denial reasons: missing BMI, missing chart notes, drug not covered for cosmetic weight loss."
                ),
                "effective_date": date(2026, 1, 1),
                "source": "Demo Policy",
                "source_url": "https://example.local/payer/demo-health-plan/wegovy",
                "criteria": [
                    "Diagnosis of obesity or overweight with comorbidity",
                    "BMI documentation",
                    "Prior lifestyle intervention documentation",
                    "Previous therapy history where applicable",
                    "Prescriber chart notes",
                ],
                "denial_reasons": [
                    "Missing BMI",
                    "Missing chart notes",
                    "Drug not covered for cosmetic weight loss",
                ],
            },
            {
                "payer_name": "Demo Health Plan",
                "therapy_area": "GLP-1",
                "drug_name": "Ozempic",
                "policy_title": "Demo Health Plan Ozempic Coverage Policy",
                "criteria_text": (
                    "Approval criteria: diagnosis of type 2 diabetes; A1c documentation; "
                    "trial, failure, or intolerance of metformin unless contraindicated; prescriber chart notes. "
                    "Denial reasons: missing A1c, missing metformin history, missing chart notes."
                ),
                "effective_date": date(2026, 1, 1),
                "source": "Demo Policy",
                "source_url": "https://example.local/payer/demo-health-plan/ozempic",
                "criteria": [
                    "Diagnosis of type 2 diabetes",
                    "A1c documentation",
                    "Metformin trial/failure/intolerance",
                    "Prescriber chart notes",
                ],
                "denial_reasons": [
                    "Missing A1c",
                    "Missing metformin history",
                    "Missing chart notes",
                ],
            },
            {
                "payer_name": "Demo Health Plan",
                "therapy_area": "GLP-1",
                "drug_name": "Mounjaro",
                "policy_title": "Demo Health Plan Mounjaro Coverage Policy",
                "criteria_text": (
                    "Approval criteria: diagnosis of type 2 diabetes; A1c documentation; "
                    "trial, failure, or intolerance of metformin unless contraindicated; prescriber chart notes."
                ),
                "effective_date": date(2026, 1, 1),
                "source": "Demo Policy",
                "source_url": "https://example.local/payer/demo-health-plan/mounjaro",
                "criteria": [
                    "Diagnosis of type 2 diabetes",
                    "A1c documentation",
                    "Metformin trial/failure/intolerance",
                    "Prescriber chart notes",
                ],
                "denial_reasons": [
                    "Missing A1c",
                    "Missing metformin history",
                    "Missing chart notes",
                ],
            },
        ]

    def find_policy(self, payer_name: str | None, drug_name: str | None) -> dict[str, Any] | None:
        normalized_drug = normalize_drug_name(drug_name)
        for policy in self.policies():
            if payer_name and policy["payer_name"].lower() != payer_name.lower():
                continue
            if policy["drug_name"].lower() == (drug_name or "").lower():
                return policy
            if normalized_drug and policy["drug_name"].lower() in {
                brand.lower() for brand in self._brands_for_generic(normalized_drug)
            }:
                return policy
        return None

    @staticmethod
    def _brands_for_generic(generic_name: str) -> list[str]:
        mapping = {
            "semaglutide": ["Ozempic", "Wegovy", "Rybelsus"],
            "tirzepatide": ["Mounjaro", "Zepbound"],
        }
        return mapping.get(generic_name, [])
