def check_for_medical_advice(text: str) -> bool:
    forbidden_phrases = ["i diagnose", "you should stop", "increase dose", "decrease dose"]
    for phrase in forbidden_phrases:
        if phrase in text.lower():
            return True
    return False
