def expand_query(query: str, role: str) -> str:
    # Simple rule-based expansion
    expanded = query
    query_lower = query.lower()
    
    if "sugar" in query_lower or "diabetes" in query_lower:
        expanded += " HbA1c blood glucose fasting postprandial"
        
    if "substitute" in query_lower or "replace" in query_lower:
        expanded += " substitution composition strength same"
        
    if role == "PATIENT":
        expanded += " explanation simple summary"
    elif role == "PHARMACIST":
        expanded += " prescription dispensing counseling missing information"
    elif role == "DOCTOR":
        expanded += " clinical summary diagnosis highlights follow-up"
        
    return expanded
