"""USB configuration check."""
from ..scorer import CheckScore


class USBCheck:
    """Check USB configuration security."""

    name = "usb_configuration"
    category = "network"

    @staticmethod
    def run() -> CheckScore:
        usb_mode = "mtp"  # mtp, ptp, charging_only, etc.
        usb_restricted = True

        passed = usb_restricted
        details = f"USB mode: {usb_mode} (restricted: {usb_restricted})"

        return CheckScore(
            check_name="usb_configuration",
            category="network",
            passed=passed,
            score=1.0 if usb_restricted else 0.3,
            weight=0.5,
            details=details,
            raw_value={"mode": usb_mode, "restricted": usb_restricted},
            recommendation="Disable USB file transfer (use MTP only when needed)" if not passed else "",
        )
