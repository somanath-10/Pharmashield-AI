from __future__ import annotations

from typing import Any

import httpx


class FDAOrangeBookConnector:
    base_url = "https://api.fda.gov/drug/drugsfda.json"

    async def search(self, drug_name: str, *, limit: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                self.base_url,
                params={"search": f"products.brand_name:\"{drug_name}\"", "limit": limit},
            )
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json().get("results", [])
