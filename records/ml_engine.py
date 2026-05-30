


class ClinicalConditionFlag:

    def __init__(self, condition, severity, message, advice, icon):
        self.condition = condition
        self.severity = severity
        self.message = message
        self.advice = advice
        self.icon = icon


class VitalsDecisionTree:



    TEMP_CRITICAL_HIGH = 40.0
    TEMP_HIGH          = 38.5
    TEMP_LOW_GRADE     = 37.5
    TEMP_HYPOTHERMIA   = 35.0


    HR_TACHYCARDIA_SEVERE = 130
    HR_TACHYCARDIA        = 100
    HR_BRADYCARDIA        = 50
    HR_BRADYCARDIA_SEVERE = 40


    SPO2_CRITICAL  = 90
    SPO2_LOW       = 94
    SPO2_BORDERLINE = 95


    GLUCOSE_HYPERGLYCEMIA_SEVERE = 11.1
    GLUCOSE_HYPERGLYCEMIA        = 7.8
    GLUCOSE_NORMAL_HIGH          = 6.1
    GLUCOSE_HYPOGLYCEMIA         = 3.9
    GLUCOSE_HYPOGLYCEMIA_SEVERE  = 2.8


    BP_HYPERTENSIVE_CRISIS = 180
    BP_STAGE2              = 160
    BP_STAGE1              = 140
    BP_ELEVATED            = 130
    BP_LOW                 = 90
    BP_CRITICAL_LOW        = 70

    def classify(self, temperature, heart_rate, oxygen_saturation,
                 blood_glucose, blood_pressure_sys):

        flags = []
        score_components = []


        if temperature is None: temp = None
        else: temp = float(temperature)
        if temp is not None and temp >= self.TEMP_CRITICAL_HIGH:
            flags.append(ClinicalConditionFlag(
                condition="Hyperpyrexia",
                severity="critical",
                message=f"Temperature {temp}°C is dangerously high (≥40°C)",
                advice="Go to A&E immediately. This is a medical emergency.",
                icon="bi-thermometer-high"
            ))
            score_components.append(40)
        elif temp >= self.TEMP_HIGH:
            flags.append(ClinicalConditionFlag(
                condition="Fever",
                severity="warning",
                message=f"Temperature {temp}°C indicates a significant fever",
                advice="Rest, stay hydrated, take paracetamol. See a doctor if it persists beyond 48 hours.",
                icon="bi-thermometer-half"
            ))
            score_components.append(25)
        elif temp >= self.TEMP_LOW_GRADE:
            flags.append(ClinicalConditionFlag(
                condition="Mild Fever",
                severity="info",
                message=f"Temperature {temp}°C is slightly elevated",
                advice="Monitor your temperature every 4 hours. Stay hydrated.",
                icon="bi-thermometer"
            ))
            score_components.append(10)
        elif temp < self.TEMP_HYPOTHERMIA:
            flags.append(ClinicalConditionFlag(
                condition="Hypothermia",
                severity="critical",
                message=f"Temperature {temp}°C is dangerously low (below 35°C)",
                advice="Seek emergency care immediately. Warm the patient gradually.",
                icon="bi-thermometer-snow"
            ))
            score_components.append(35)


        if heart_rate is None: hr = None
        else: hr = int(heart_rate)
        if hr is not None and hr >= self.HR_TACHYCARDIA_SEVERE:
            flags.append(ClinicalConditionFlag(
                condition="Severe Tachycardia",
                severity="critical",
                message=f"Heart rate {hr} bpm is severely elevated",
                advice="Seek immediate medical attention. This may indicate cardiac stress.",
                icon="bi-heart-pulse-fill"
            ))
            score_components.append(35)
        elif hr >= self.HR_TACHYCARDIA:
            flags.append(ClinicalConditionFlag(
                condition="Tachycardia",
                severity="warning",
                message=f"Heart rate {hr} bpm is above normal (>100 bpm)",
                advice="Rest and avoid strenuous activity. See a doctor if this continues.",
                icon="bi-heart-pulse"
            ))
            score_components.append(20)
        elif hr <= self.HR_BRADYCARDIA_SEVERE:
            flags.append(ClinicalConditionFlag(
                condition="Severe Bradycardia",
                severity="critical",
                message=f"Heart rate {hr} bpm is critically low",
                advice="Seek emergency care immediately.",
                icon="bi-heart"
            ))
            score_components.append(40)
        elif hr <= self.HR_BRADYCARDIA:
            flags.append(ClinicalConditionFlag(
                condition="Bradycardia",
                severity="warning",
                message=f"Heart rate {hr} bpm is below normal (<60 bpm)",
                advice="Consult a doctor, especially if you feel dizzy or faint.",
                icon="bi-heart"
            ))
            score_components.append(15)

        if oxygen_saturation is None: spo2 = None
        else: spo2 = int(oxygen_saturation)
        if spo2 is not None and spo2 <= self.SPO2_CRITICAL:
            flags.append(ClinicalConditionFlag(
                condition="Critical Hypoxia",
                severity="critical",
                message=f"Oxygen level {spo2}% is critically low (≤90%)",
                advice="Emergency oxygen therapy needed. Go to A&E now.",
                icon="bi-lungs-fill"
            ))
            score_components.append(45)
        elif spo2 <= self.SPO2_LOW:
            flags.append(ClinicalConditionFlag(
                condition="Low Oxygen",
                severity="warning",
                message=f"Oxygen level {spo2}% is below normal (94-95%)",
                advice="See a doctor today. Avoid physical exertion.",
                icon="bi-lungs"
            ))
            score_components.append(25)
        elif spo2 <= self.SPO2_BORDERLINE:
            flags.append(ClinicalConditionFlag(
                condition="Borderline Oxygen",
                severity="info",
                message=f"Oxygen level {spo2}% is slightly low",
                advice="Monitor closely. Breathe deeply and rest.",
                icon="bi-lungs"
            ))
            score_components.append(10)


        if blood_glucose is None: glucose = None
        else: glucose = float(blood_glucose)
        if glucose is not None and glucose >= self.GLUCOSE_HYPERGLYCEMIA_SEVERE:
            flags.append(ClinicalConditionFlag(
                condition="Hyperglycemia",
                severity="critical",
                message=f"Blood glucose {glucose} mmol/L is critically high",
                advice="Seek medical attention immediately. Possible diabetic crisis.",
                icon="bi-droplet-fill"
            ))
            score_components.append(35)
        elif glucose >= self.GLUCOSE_HYPERGLYCEMIA:
            flags.append(ClinicalConditionFlag(
                condition="Elevated Blood Sugar",
                severity="warning",
                message=f"Blood glucose {glucose} mmol/L is above normal",
                advice="Consult your doctor. Reduce sugar intake and exercise regularly.",
                icon="bi-droplet-half"
            ))
            score_components.append(20)
        elif glucose >= self.GLUCOSE_NORMAL_HIGH:
            flags.append(ClinicalConditionFlag(
                condition="Pre-Diabetic Range",
                severity="info",
                message=f"Blood glucose {glucose} mmol/L is in the pre-diabetic range",
                advice="Consider dietary changes. Monitor regularly and see a doctor.",
                icon="bi-droplet"
            ))
            score_components.append(10)
        elif glucose <= self.GLUCOSE_HYPOGLYCEMIA_SEVERE:
            flags.append(ClinicalConditionFlag(
                condition="Severe Hypoglycemia",
                severity="critical",
                message=f"Blood glucose {glucose} mmol/L is critically low",
                advice="Consume sugar immediately. Seek emergency care.",
                icon="bi-droplet-fill"
            ))
            score_components.append(40)
        elif glucose <= self.GLUCOSE_HYPOGLYCEMIA:
            flags.append(ClinicalConditionFlag(
                condition="Low Blood Sugar",
                severity="warning",
                message=f"Blood glucose {glucose} mmol/L is below normal",
                advice="Have a meal or sugary drink. Monitor and see a doctor.",
                icon="bi-droplet-half"
            ))
            score_components.append(20)


        if blood_pressure_sys is None: bp = None
        else: bp = int(blood_pressure_sys)
        if bp is not None and bp >= self.BP_HYPERTENSIVE_CRISIS:
            flags.append(ClinicalConditionFlag(
                condition="Hypertensive Crisis",
                severity="critical",
                message=f"Blood pressure {bp} mmHg is in hypertensive crisis range",
                advice="Emergency: Go to hospital immediately. Risk of stroke.",
                icon="bi-activity"
            ))
            score_components.append(45)
        elif bp >= self.BP_STAGE2:
            flags.append(ClinicalConditionFlag(
                condition="Stage 2 Hypertension",
                severity="critical",
                message=f"Blood pressure {bp} mmHg indicates Stage 2 hypertension",
                advice="See a doctor urgently. You may need medication.",
                icon="bi-activity"
            ))
            score_components.append(30)
        elif bp >= self.BP_STAGE1:
            flags.append(ClinicalConditionFlag(
                condition="Stage 1 Hypertension",
                severity="warning",
                message=f"Blood pressure {bp} mmHg indicates Stage 1 hypertension",
                advice="Monitor daily. Reduce salt, exercise, see a doctor.",
                icon="bi-activity"
            ))
            score_components.append(20)
        elif bp >= self.BP_ELEVATED:
            flags.append(ClinicalConditionFlag(
                condition="Elevated Blood Pressure",
                severity="info",
                message=f"Blood pressure {bp} mmHg is slightly elevated",
                advice="Lifestyle changes recommended. Monitor regularly.",
                icon="bi-activity"
            ))
            score_components.append(10)
        elif bp <= self.BP_CRITICAL_LOW:
            flags.append(ClinicalConditionFlag(
                condition="Hypotensive Shock",
                severity="critical",
                message=f"Blood pressure {bp} mmHg is critically low",
                advice="Emergency care needed immediately.",
                icon="bi-activity"
            ))
            score_components.append(45)
        elif bp <= self.BP_LOW:
            flags.append(ClinicalConditionFlag(
                condition="Low Blood Pressure",
                severity="warning",
                message=f"Blood pressure {bp} mmHg is below normal",
                advice="Sit or lie down. Drink fluids. See a doctor if dizzy.",
                icon="bi-activity"
            ))
            score_components.append(15)


        confidence_score = min(sum(score_components), 100)


        critical_flags = [f for f in flags if f.severity == 'critical']
        warning_flags  = [f for f in flags if f.severity == 'warning']

        if critical_flags:
            summary = f"{len(critical_flags)} critical condition(s) detected — seek care immediately."
            overall_severity = 'critical'
        elif warning_flags:
            summary = f"{len(warning_flags)} condition(s) need attention — consult a doctor."
            overall_severity = 'warning'
        elif flags:
            summary = "Minor variations noted — monitor and follow up if needed."
            overall_severity = 'info'
        else:
            summary = "All vitals are within normal range. Keep it up!"
            overall_severity = 'normal'

        return {
            'flags':            flags,
            'confidence_score': confidence_score,
            'summary':          summary,
            'overall_severity': overall_severity,
            'needs_scan':       confidence_score >= 80,
            'critical_count':   len(critical_flags),
            'warning_count':    len(warning_flags),
        }



_tree = VitalsDecisionTree()

def analyse_vitals(temperature, heart_rate, oxygen_saturation,
                   blood_glucose, blood_pressure_sys):

    return _tree.classify(
        temperature, heart_rate, oxygen_saturation,
        blood_glucose, blood_pressure_sys
    )