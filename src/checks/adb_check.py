"""ADB debugging check."""
from ..scorer import CheckScore


class ADBCheck:
    """Check ADB debugging status."""

    name = "adb_debugging"
    category = "network"

    @staticmethod
    def run() -> CheckScore:
        adb_enabled = False  # Would check persist.sys.usb.config
        adb_over_network = False

        passed = not adb_enabled
        details = "ADB disabled" if not adb_enabled else "ADB enabled (security risk)"

        return CheckScore(
            check_name="adb_debugging",
            category="network",
            passed=passed,
            score=1.0 if not adb_enabled else 0.0,
            weight=0.5,
            details=details,
            raw_value={"adb_enabled": adb_enabled, "adb_over_network": adb_over_network},
            recommendation="Disable ADB debugging when not in use" if not passed else "",
        )
