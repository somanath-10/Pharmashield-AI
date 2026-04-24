from __future__ import annotations

from app.schemas.case import CaseAnalyzeRequest


class MemoryPolicy:
    def scopes_for_request(self, request: CaseAnalyzeRequest) -> list[tuple[str, str]]:
        scopes = [("GLOBAL", "global")]
        if request.inventory_context.location_id:
            scopes.append(("PHARMACY_LOCATION", request.inventory_context.location_id))
        if request.payer_name:
            scopes.append(("PAYER", request.payer_name))
        if request.drug_name:
            scopes.append(("DRUG", request.drug_name))
        if request.product_context.supplier_name:
            scopes.append(("SUPPLIER", request.product_context.supplier_name))
        return scopes
