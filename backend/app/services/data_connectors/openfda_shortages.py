from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenFDAShortagesConnector:
    base_url = "https://api.fda.gov/drug/shortages.json"

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def search(
        self,
        *,
        drug_name: str,
        limit: int = 5,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        params = {
            "search": f"(generic_name:\"{drug_name}\" OR brand_name:\"{drug_name}\")",
            "limit": limit,
            "skip": skip,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(self.base_url, params=params)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return [self.normalize(item) for item in response.json().get("results", [])]

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "drug_name": payload.get("brand_name") or payload.get("generic_name") or "unknown",
            "generic_name": payload.get("generic_name"),
            "status": payload.get("status") or payload.get("current_status"),
            "reason": payload.get("reason"),
            "therapeutic_category": payload.get("therapeutic_category"),
            "source": "openFDA",
            "source_url": self.base_url,
            "initial_posting_date": self._parse_date(payload.get("initial_posting_date")),
            "last_updated": self._parse_date(payload.get("updated_date")),
            "raw_payload_json": payload,
        }

    @staticmethod
    def _parse_date(raw: str | None) -> datetime | None:
        if not raw:
            return None
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return None
