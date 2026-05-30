def calculate_patient_risk(vitals):
    score = 0

    if float(vitals.temperature) > 38.5:
        score += 25
    if int(vitals.oxygen_saturation) < 92:
        score += 40
    if float(vitals.blood_glucose or 0) > 7.0:
        score += 20
    if int(vitals.heart_rate) > 100:
        score += 15

    if score >= 80:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 20:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "score": min(score, 100),
        "risk_level": level
    }
def get_recommendation(vitals):
    if int(vitals.oxygen_saturation) < 92:
        return "Low oxygen detected — urgent care recommended"

    if float(vitals.temperature) > 38:
        return "Possible infection — doctor review advised"

    if int(vitals.heart_rate) > 100:
        return "Elevated heart rate — monitor closely"

    return "No immediate concern"
def detect_trend(records):
    if len(records) < 2:
        return "stable"

    latest = records[0]
    previous = records[1]

    if latest.heart_rate > previous.heart_rate:
        return "increasing"

    if latest.heart_rate < previous.heart_rate:
        return "decreasing"

    return "stable"