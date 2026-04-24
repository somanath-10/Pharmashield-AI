from __future__ import annotations

from app.core.constants import GLP1_QUERY_EXPANSIONS, drug_aliases, normalize_drug_name


class QueryExpansionService:
    def expand(self, query: str, drug_name: str | None = None) -> list[str]:
        expansions = {query.strip()}
        normalized = normalize_drug_name(drug_name)
        if normalized:
            expansions.update(drug_aliases(normalized))
        lower_query = query.lower()
        if any(term in lower_query for term in ("ozempic", "wegovy", "semaglutide", "tirzepatide", "glp-1")):
            expansions.update(GLP1_QUERY_EXPANSIONS)
        return [item for item in expansions if item]
