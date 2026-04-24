from __future__ import annotations


class ComplianceGuardrail:
    def validate_actions(self, actions: list[str]) -> list[str]:
        cleaned: list[str] = []
        for action in actions:
            updated = action.strip()
            if "online supplier" in updated.lower() and "do not" not in updated.lower():
                updated = "Do not recommend patient-provided online supplier until verified."
            cleaned.append(updated)
        return cleaned
