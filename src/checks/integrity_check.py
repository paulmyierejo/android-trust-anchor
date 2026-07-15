"""System integrity check."""
import os
from ..scorer import CheckScore


class IntegrityCheck:
    """Check system partition integrity."""

    name = "system_integrity"
    category = "integrity"

    CRITICAL_SYSTEM_FILES = [
        "/system/bin/run-as",
        "/system/lib64/libandroid_runtime.so",
    ]

    @staticmethod
    def run() -> CheckScore:
        missing = [f for f in IntegrityCheck.CRITICAL_SYSTEM_FILES
                   if not os.path.exists(f)]
        passed = len(missing) == 0

        return CheckScore(
            check_name="system_integrity",
            category="integrity",
            passed=passed,
            score=1.0 if passed else 0.0,
            weight=1.0,
            details=f"System integrity OK" if passed else f"{len(missing)} critical files missing",
            raw_value={"missing_files": missing},
            recommendation="Reflash stock firmware" if not passed else "",
        )
