from __future__ import annotations

from app.core.constants import PHARMACIST_REVIEW_DISCLAIMER


class MedicalSafetyGuardrail:
    banned_phrases = {
        "safe for this patient": "may be appropriate pending pharmacist or clinician review",
        "switch immediately": "consider prescriber-reviewed substitution workflow",
        "use the online supplier": "verify regulated supply chain before any recommendation",
    }

    def enforce(self, text: str) -> str:
        output = text
        for banned, replacement in self.banned_phrases.items():
            output = output.replace(banned, replacement)
        if PHARMACIST_REVIEW_DISCLAIMER not in output:
            output = f"{output}\n\n{PHARMACIST_REVIEW_DISCLAIMER}"
        return output
