def validate_patient_output(output: dict) -> dict:
    disclaimer = "This explanation is for understanding only. It is not a diagnosis or prescription. Please consult your doctor or pharmacist before making any medical decision."
    output["disclaimer"] = disclaimer
    return output
