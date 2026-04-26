def expand_query(query: str, role: str) -> str:
    """Expand query with India-specific pharmacy intelligence terms."""
    expanded = query
    q = query.lower()

    # General clinical terms
    if "sugar" in q or "diabetes" in q:
        expanded += " HbA1c blood glucose fasting postprandial metformin"
    if "substitute" in q or "replace" in q or "alternative" in q:
        expanded += " substitution composition strength same generic"
    if "cheap" in q or "affordable" in q or "budget" in q or "generic" in q:
        expanded += " Jan Aushadhi NPPA price ceiling MRP generic composition"
    if "augmentin" in q or "amoxicillin" in q:
        expanded += " Amoxicillin Clavulanic Acid Schedule H1 antibiotic"
    if "batch" in q or "nsq" in q or "spurious" in q:
        expanded += " CDSCO NSQ batch manufacturer expiry quality alert"
    if "whatsapp" in q or "online" in q or "instagram" in q:
        expanded += " online seller license risk suspicious no prescription"
    if "ayushman" in q or "pm-jay" in q or "pmjay" in q:
        expanded += " PM-JAY hospitalization empanelled hospital cashless scheme"
    if "cghs" in q:
        expanded += " CGHS Central Government Health Scheme reimbursement"
    if "prescription" in q or "schedule" in q:
        expanded += " Schedule H H1 X prescription dispensing compliance"

    # Role-specific additions
    if role == "PATIENT":
        expanded += " simple explanation summary medicine lab report"
    elif role == "PHARMACIST":
        expanded += " dispensing compliance counseling substitution stock"
    elif role == "DOCTOR":
        expanded += " clinical summary diagnosis highlights follow-up"
    elif role == "ADMIN":
        expanded += " analytics risk overview high risk cases"

    return expanded
