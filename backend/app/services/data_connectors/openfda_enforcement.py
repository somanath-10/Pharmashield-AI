from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenFDAEnforcementConnector:
    base_url = "https://api.fda.gov/drug/enforcement.json"

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def search(
        self,
        *,
        product_description: str | None = None,
        recalling_firm: str | None = None,
        classification: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        clauses = []
        if product_description:
            clauses.append(f'product_description:"{product_description}"')
        if recalling_firm:
            clauses.append(f'recalling_firm:"{recalling_firm}"')
        if classification:
            clauses.append(f'classification:"{classification}"')
        if not clauses:
            return []
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                self.base_url,
                params={"search": " AND ".join(clauses), "limit": limit},
            )
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return [self.normalize(item) for item in response.json().get("results", [])]

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "drug_name": payload.get("product_description") or "unknown",
            "classification": payload.get("classification"),
            "reason_for_recall": payload.get("reason_for_recall"),
            "recalling_firm": payload.get("recalling_firm"),
            "distribution_pattern": payload.get("distribution_pattern"),
            "product_description": payload.get("product_description"),
            "code_info": payload.get("code_info"),
            "source": "openFDA",
            "source_url": self.base_url,
            "raw_payload_json": payload,
        }
