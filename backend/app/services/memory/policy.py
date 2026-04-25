from __future__ import annotations

from app.schemas.case import CaseAnalyzeRequest


class MemoryPolicy:
    def scopes_for_request(self, request: CaseAnalyzeRequest) -> list[tuple[str, str]]:
        scopes = [("GLOBAL", "global")]
        if request.inventory_context.location_id:
            scopes.append(("PHARMACY_LOCATION", request.inventory_context.location_id))
        if request.location_state:
            scopes.append(("STATE", request.location_state))
        if request.drug_name:
            scopes.append(("DRUG", request.drug_name))
        if request.brand_name:
            scopes.append(("BRAND", request.brand_name))
        if request.product_context.seller_name:
            scopes.append(("SELLER", request.product_context.seller_name))
        return scopes
