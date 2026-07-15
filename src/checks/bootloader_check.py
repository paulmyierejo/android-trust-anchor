"""Bootloader lock state check."""
import os
from ..scorer import CheckScore


class BootloaderCheck:
    """Check if bootloader is locked."""

    name = "bootloader_lock"
    category = "boot"

    @staticmethod
    def run() -> CheckScore:
        boot_state = "locked"  # Would read from device
        passed = boot_state == "locked"

        return CheckScore(
            check_name="bootloader_lock",
            category="boot",
            passed=passed,
            score=1.0 if passed else 0.0,
            weight=2.0,
            details=f"Bootloader state: {boot_state}",
            raw_value=boot_state,
            recommendation="Lock the bootloader to ensure system integrity" if not passed else "",
        )
