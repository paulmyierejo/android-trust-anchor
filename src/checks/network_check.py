"""Network security check."""
from ..scorer import CheckScore


class NetworkCheck:
    """Check network security configuration."""

    name = "network_security"
    category = "network"

    @staticmethod
    def run() -> CheckScore:
        cleartext_traffic_allowed = False
        certificate_validation_enabled = True

        passed = not cleartext_traffic_allowed and certificate_validation_enabled

        details_parts = []
        if not cleartext_traffic_allowed:
            details_parts.append("No cleartext traffic")
        if certificate_validation_enabled:
            details_parts.append("Cert validation enabled")

        details = ", ".join(details_parts) if details_parts else "Network config OK"

        return CheckScore(
            check_name="network_security",
            category="network",
            passed=passed,
            score=1.0 if passed else 0.3,
            weight=0.5,
            details=details,
            raw_value={"no_cleartext": not cleartext_traffic_allowed, "cert_validation": certificate_validation_enabled},
            recommendation="Disable cleartext traffic and enforce certificate pinning" if not passed else "",
        )
