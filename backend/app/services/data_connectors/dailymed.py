from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class DailyMedConnector:
    base_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def search_spls(self, drug_name: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/spls.json", params={"drug_name": drug_name})
        response.raise_for_status()
        return response.json().get("data", []) or response.json().get("results", [])

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
    async def fetch_label_metadata(self, setid: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{self.base_url}/spls/{setid}.json")
        response.raise_for_status()
        return response.json().get("data", {})

    async def fetch_relevant_sections(self, setid: str) -> list[dict[str, Any]]:
        metadata = await self.fetch_label_metadata(setid)
        sections = metadata.get("sections", []) or []
        normalized = []
        wanted_sections = {
            "indications_and_usage",
            "dosage_and_administration",
            "contraindications",
            "warnings_and_precautions",
            "adverse_reactions",
            "drug_interactions",
            "patient_counseling_information",
        }
        for section in sections:
            title = str(section.get("title", "")).lower().replace(" ", "_")
            if title in wanted_sections:
                normalized.append(
                    {
                        "section": title,
                        "text": section.get("text") or section.get("content") or "",
                    }
                )
        return normalized
