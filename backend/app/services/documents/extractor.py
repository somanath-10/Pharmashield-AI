import re
from typing import List, Dict, Any

def extract_medicines(text: str) -> List[Dict[str, Any]]:
    # Simple rule-based extraction for MVP
    medicines = []
    common_meds = ["Metformin", "Augmentin", "Amoxicillin", "Paracetamol", "Pantoprazole"]
    for med in common_meds:
        if med.lower() in text.lower():
            medicines.append({
                "medicine_name": med,
                "strength": "Unknown",
                "dosage_form": "tablet",
                "frequency": "Unknown",
                "duration": "Unknown",
                "instructions": "Unknown"
            })
    return medicines

def extract_lab_values(text: str) -> List[Dict[str, Any]]:
    # Simple rule-based extraction for MVP
    lab_values = []
    common_tests = ["HbA1c", "Fasting Blood Sugar", "Hemoglobin", "Creatinine", "WBC"]
    for test in common_tests:
        if test.lower() in text.lower():
            lab_values.append({
                "test_name": test,
                "test_value": "Unknown",
                "unit": "Unknown",
                "reference_range": "Unknown",
                "flag": "UNKNOWN"
            })
    return lab_values
