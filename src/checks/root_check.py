"""Root detection check."""
import os
from ..scorer import CheckScore


class RootCheck:
    """Detect if device is rooted."""

    name = "root_detection"
    category = "integrity"

    SU_PATHS = [
        "/system/app/Superuser.apk",
        "/sbin/su", "/system/bin/su", "/system/xbin/su",
        "/data/local/xbin/su",
    ]

    @staticmethod
    def run() -> CheckScore:
        indicators = [p for p in RootCheck.SU_PATHS if os.path.exists(p)]
        passed = len(indicators) == 0

        return CheckScore(
            check_name="root_detection",
            category="integrity",
            passed=passed,
            score=1.0 if passed else 0.0,
            weight=2.0,
            details=f"Found {len(indicators)} root indicators" if indicators else "No root detected",
            raw_value={"indicator_count": len(indicators), "paths": indicators},
            recommendation="Rooted device — do not use for sensitive operations" if not passed else "",
        )
