"""OTA/security patch check."""
from ..scorer import CheckScore


class OTACheck:
    """Check OTA update and security patch status."""

    name = "security_patch"
    category = "software"

    MIN_SECURITY_PATCH_MONTHS = 2  # Device should have patch within last 2 months

    @staticmethod
    def run() -> CheckScore:
        from datetime import datetime

        current_patch = "2024-01"  # Would read from device
        # Parse to datetime
        patch_date = datetime(2024, 1, 1)
        age_months = (datetime.now() - patch_date).days / 30
        passed = age_months <= OTACheck.MIN_SECURITY_PATCH_MONTHS

        return CheckScore(
            check_name="security_patch",
            category="software",
            passed=passed,
            score=1.0 if age_months <= 1 else 0.5 if age_months <= 3 else 0.0,
            weight=1.0,
            details=f"Security patch: {current_patch} ({age_months:.1f} months old)",
            raw_value={"patch_date": current_patch, "age_months": age_months},
            recommendation="Install latest security update" if not passed else "",
        )
