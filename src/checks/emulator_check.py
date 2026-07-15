"""Emulator detection check."""
import os
from ..scorer import CheckScore


class EmulatorCheck:
    """Detect Android emulator/QEMU environment."""

    name = "emulator_detection"
    category = "integrity"

    EMULATOR_MARKERS = [
        "/init.goldfish.rc", "/init.x86_64.rc",
        "/dev/qemu_pipe", "/dev/hwfifo",
        "/system/lib/qemuProps",
        "/system/bin/nox", "/system/bin/blueStacks",
    ]

    @staticmethod
    def run() -> CheckScore:
        indicators = [p for p in EmulatorCheck.EMULATOR_MARKERS if os.path.exists(p)]
        passed = len(indicators) == 0

        return CheckScore(
            check_name="emulator_detection",
            category="integrity",
            passed=passed,
            score=1.0 if passed else 0.0,
            weight=1.5,
            details=f"Found {len(indicators)} emulator markers" if indicators else "No emulator detected",
            raw_value={"indicator_count": len(indicators)},
            recommendation="Do not use emulator for sensitive operations" if not passed else "",
        )
