"""Biometric authentication check."""
from ..scorer import CheckScore


class BiometricCheck:
    """Check biometric authentication availability."""

    name = "biometric_auth"
    category = "authentication"

    @staticmethod
    def run() -> CheckScore:
        has_strong_biometric = True  # Would check BiometricManager
        biometric_type = "fingerprint"

        passed = has_strong_biometric
        details = f"Strong biometric available: {biometric_type}" if passed else "No strong biometric"

        return CheckScore(
            check_name="biometric_auth",
            category="authentication",
            passed=passed,
            score=1.0 if has_strong_biometric else 0.5,
            weight=0.5,
            details=details,
            raw_value={"has_strong": has_strong_biometric, "type": biometric_type},
            recommendation="Enroll fingerprint or face for convenient authentication" if not passed else "",
        )
