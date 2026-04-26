from typing import Any, Dict, List
from app.models.domain import Case

class AdminAgent:
    """
    Admin Agent returns aggregated system insights across all roles.
    """
    
    async def analyze(self, case: Case, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Live aggregation from MongoDB
        all_cases = await Case.find_all().to_list()
        total = len(all_cases)
        high_risk = sum(1 for c in all_cases if c.risk_level in ("HIGH", "CRITICAL"))
        medium_risk = sum(1 for c in all_cases if c.risk_level == "MEDIUM")
        by_role = {}
        for c in all_cases:
            r = c.role.value
            by_role[r] = by_role.get(r, 0) + 1

        return {
            "insights": "Admin analytics summary generated from live case data.",
            "metrics": {
                "total_cases": total,
                "high_risk_cases": high_risk,
                "medium_risk_cases": medium_risk,
                "cases_by_role": by_role,
            },
            "recommendation": "Review all HIGH/CRITICAL risk cases and escalate as needed.",
            "disclaimer": "Admin review mode active. Analytics are AI-generated aggregates.",
        }
