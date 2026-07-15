"""Full-disk/File-based encryption check."""
import os
from ..scorer import CheckScore


class EncryptionCheck:
    """Check device encryption status."""

    name = "device_encryption"
    category = "encryption"

    @staticmethod
    def run() -> CheckScore:
        encryption_type = "none"
        details = "Encryption status unknown"

        # Check for FDE metadata
        fde_path = "/data/unencrypted/key"
        fbe_indicator = "/data/system/gatekeeper.password.key"

        if os.path.exists(fbe_indicator) or os.path.exists("/data/system_de/0"):
            encryption_type = "fbe"
            details = "File-Based Encryption (FBE) detected"
        elif os.path.exists(fde_path):
            encryption_type = "fde"
            details = "Full-Disk Encryption (FDE) detected"
        else:
            # Check ro.crypto.state property
            # Would read from getprop or property files
            encryption_type = "unknown"
            details = "No encryption metadata found"

        # FBE is preferred over FDE
        passed = encryption_type in ("fbe", "fde")

        return CheckScore(
            check_name="device_encryption",
            category="encryption",
            passed=passed,
            score=1.0 if encryption_type == "fbe" else 0.5 if encryption_type == "fde" else 0.0,
            weight=1.5,
            details=details,
            raw_value=encryption_type,
            recommendation="Enable device encryption for data protection" if not passed else "",
        )
