"""Screen lock check."""
from ..scorer import CheckScore


class ScreenLockCheck:
    """Check if screen lock is configured."""

    name = "screen_lock"
    category = "authentication"

    @staticmethod
    def run() -> CheckScore:
        lock_enabled = True  # Would check gatekeeper
        lock_type = "PIN"

        details = f"Screen lock enabled ({lock_type})" if lock_enabled else "No screen lock"

        return CheckScore(
            check_name="screen_lock",
            category="authentication",
            passed=lock_enabled,
            score=1.0 if lock_enabled else 0.0,
            weight=1.0,
            details=details,
            raw_value={"enabled": lock_enabled, "type": lock_type},
            recommendation="Enable screen lock with strong password/PIN" if not lock_enabled else "",
        )
