"""Debug flags check."""
import os
from ..scorer import CheckScore


class DebugCheck:
    """Check debug system flags."""

    name = "debug_flags"
    category = "integrity"

    @staticmethod
    def run() -> CheckScore:
        debuggable = False
        details = "No debug flags detected"

        build_prop = "/system/build.prop"
        if os.path.exists(build_prop):
            try:
                with open(build_prop) as f:
                    content = f.read()
                    if "ro.debuggable=1" in content:
                        debuggable = True
                        details = "Device is debuggable (ro.debuggable=1)"
            except Exception:
                pass

        passed = not debuggable
        return CheckScore(
            check_name="debug_flags",
            category="integrity",
            passed=passed,
            score=1.0 if not debuggable else 0.0,
            weight=1.0,
            details=details,
            raw_value=debuggable,
            recommendation="Disable debug flags in production builds" if not passed else "",
        )
