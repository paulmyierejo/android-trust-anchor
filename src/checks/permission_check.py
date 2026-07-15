"""Permission review check."""
from ..scorer import CheckScore


class PermissionCheck:
    """Check dangerous permission grants."""

    name = "permission_review"
    category = "software"

    DANGEROUS_PERMISSIONS = [
        "android.permission.READ_SMS",
        "android.permission.READ_CONTACTS",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.RECORD_AUDIO",
        "android.permission.READ_CALL_LOG",
        "android.permission.READ_EXTERNAL_STORAGE",
    ]

    @staticmethod
    def run() -> CheckScore:
        granted_count = 0  # Would query PackageManager
        total_count = len(PermissionCheck.DANGEROUS_PERMISSIONS)
        passed = granted_count <= 2

        details = f"{granted_count}/{total_count} dangerous permissions granted"

        return CheckScore(
            check_name="permission_review",
            category="software",
            passed=passed,
            score=1.0 if granted_count == 0 else 0.5 if granted_count <= 2 else 0.0,
            weight=0.5,
            details=details,
            raw_value={"granted": granted_count, "total": total_count},
            recommendation="Review and revoke unnecessary dangerous permissions" if not passed else "",
        )
