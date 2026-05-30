import time
import random


def mock_cnn_analysis(image_path):
    # This simulates the time it takes for a real AI to think
    time.sleep(2)

    results = [
        "Analysis Complete: No significant anomalies detected in the scan.",
        "Analysis Complete: Potential inflammation observed. Please consult a specialist.",
        "Analysis Complete: Image clarity is low. Please re-upload for better accuracy."
    ]

    # Randomly pick a result so your demo looks "live"
    return random.choice(results)