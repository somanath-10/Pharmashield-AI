from __future__ import annotations

from collections.abc import Iterable

SUPPORTED_GLP1_DRUGS = {
    "semaglutide": {
        "generic_name": "semaglutide",
        "brands": ["Ozempic", "Wegovy", "Rybelsus"],
    },
    "tirzepatide": {
        "generic_name": "tirzepatide",
        "brands": ["Mounjaro", "Zepbound"],
    },
}

GENERIC_TO_BRANDS = {
    generic: details["brands"] for generic, details in SUPPORTED_GLP1_DRUGS.items()
}

BRAND_TO_GENERIC = {
    brand.lower(): details["generic_name"]
    for details in SUPPORTED_GLP1_DRUGS.values()
    for brand in details["brands"]
}

GLP1_QUERY_EXPANSIONS = [
    "semaglutide",
    "tirzepatide",
    "Ozempic",
    "Wegovy",
    "Rybelsus",
    "Mounjaro",
    "Zepbound",
    "GLP-1",
    "prior authorization",
    "coverage criteria",
    "drug shortage",
    "compounded semaglutide",
    "counterfeit Ozempic",
    "unapproved GLP-1",
    "supplier verification",
]

SUSPICIOUS_PRODUCT_CLAIMS = [
    "generic ozempic",
    "same as ozempic",
    "no prescription needed",
    "research use only",
    "compounded fda-approved",
    "fda-approved compounded semaglutide",
    "cheap semaglutide online",
    "weight loss injection without doctor",
]

SHORTAGE_TERMS = {"out of stock", "shortage", "unavailable", "inventory", "backorder"}
RECALL_TERMS = {"recall", "lot", "affected product"}
PA_TERMS = {"denied", "prior auth", "prior authorization", "pa", "insurance", "payer", "coverage", "formulary"}
AUTHENTICITY_TERMS = {"online supplier", "counterfeit", "no prescription", "compounded", "generic ozempic", "semaglutide source"}

SOURCE_PRIORITY = {
    "internal_sop": 5.0,
    "payer_policy": 4.5,
    "openfda": 4.0,
    "dailymed": 4.0,
    "demo_policy": 3.5,
    "general_note": 2.0,
}

SECTION_PRIORITY = {
    "warnings": 3.0,
    "warnings_and_precautions": 3.0,
    "contraindications": 3.0,
    "approval_criteria": 2.8,
    "denial_reasons": 2.7,
    "patient_counseling": 2.5,
    "shortage_status": 2.4,
    "unsafe_claims": 2.3,
}

RISK_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

PHARMACIST_REVIEW_DISCLAIMER = (
    "Pharmacist review required before clinical, dispensing, substitution, "
    "or patient-specific action."
)


def normalize_drug_name(name: str | None) -> str:
    if not name:
        return ""
    cleaned = name.strip()
    if not cleaned:
        return ""
    generic = BRAND_TO_GENERIC.get(cleaned.lower())
    return generic or cleaned.lower()


def drug_aliases(name: str | None) -> list[str]:
    normalized = normalize_drug_name(name)
    if not normalized:
        return []
    aliases = {normalized}
    if normalized in GENERIC_TO_BRANDS:
        aliases.update(brand.lower() for brand in GENERIC_TO_BRANDS[normalized])
    brand_generic = BRAND_TO_GENERIC.get(normalized)
    if brand_generic:
        aliases.add(brand_generic)
    return sorted(aliases)


def flatten_terms(*groups: Iterable[str]) -> list[str]:
    values: set[str] = set()
    for group in groups:
        values.update(term.lower() for term in group)
    return sorted(values)
