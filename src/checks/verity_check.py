"""DM-verity check."""
import os
from ..scorer import CheckScore


class VerityCheck:
    """Check dm-verity enforcement status."""

    name = "dm_verity"
    category = "boot"

    @staticmethod
    def run() -> CheckScore:
        verity_enabled = False
        details = "Could not determine verity status"

        mounts_path = "/proc/mounts"
        if os.path.exists(mounts_path):
            try:
                with open(mounts_path) as f:
                    for line in f:
                        if "/system" in line and "verity" in line:
                            verity_enabled = True
                            details = "dm-verity is enabled for /system"
                            break
            except Exception:
                pass

        if not verity_enabled:
            details = "dm-verity not detected for /system"

        return CheckScore(
            check_name="dm_verity",
            category="boot",
            passed=verity_enabled,
            score=1.0 if verity_enabled else 0.0,
            weight=1.5,
            details=details,
            raw_value=verity_enabled,
            recommendation="Enable dm-verity for system partition integrity" if not verity_enabled else "",
        )
