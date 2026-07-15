"""SELinux enforcement check."""
import os
from ..scorer import CheckScore


class SELinuxCheck:
    """Check SELinux enforcement status."""

    name = "selinux_enforcing"
    category = "integrity"

    @staticmethod
    def run() -> CheckScore:
        enforcing = False
        details = "Could not determine SELinux state"

        enforce_path = "/sys/fs/selinux/enforce"
        if os.path.exists(enforce_path):
            try:
                with open(enforce_path) as f:
                    enforcing = f.read().strip() == "1"
                    details = "Enforcing" if enforcing else "Permissive"
            except Exception:
                details = "SELinux file readable but could not parse"

        return CheckScore(
            check_name="selinux_enforcing",
            category="integrity",
            passed=enforcing,
            score=1.0 if enforcing else 0.0,
            weight=1.5,
            details=details,
            raw_value=enforcing,
            recommendation="Set SELinux to enforcing mode" if not enforcing else "",
        )
