"""
Android Device Trust Assessment Scoring Engine
Combines all security checks into a unified trust score (0-100)
with detailed breakdown by category.
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TrustLevel(Enum):
    """Overall trust level classification."""
    TRUSTED = "trusted"           # 80-100: Fully trusted
    ACCEPTABLE = "acceptable"      # 60-79: Generally acceptable with caveats
    CAUTION = "caution"            # 40-59: Proceed with care
    HIGH_RISK = "high_risk"        # 20-39: Significant concerns
    UNTRUSTED = "untrusted"        # 0-19: Do not trust


@dataclass
class CheckScore:
    """Score for a single security check."""
    check_name: str
    category: str
    passed: bool
    score: float          # 0.0 to 1.0
    weight: float         # Relative importance
    details: str = ""
    raw_value: Any = None
    recommendation: str = ""

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class CategoryScore:
    """Aggregated score for a category of checks."""
    name: str
    description: str
    checks: List[CheckScore] = field(default_factory=list)
    weight: float = 1.0

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.checks)

    @property
    def category_score(self) -> float:
        if not self.checks:
            return 0.0
        total_weight = self.total_weight
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(c.weighted_score for c in self.checks)
        return weighted_sum / total_weight

    @property
    def pass_rate(self) -> float:
        if not self.checks:
            return 0.0
        passed = sum(1 for c in self.checks if c.passed)
        return passed / len(self.checks)


@dataclass
class TrustAssessment:
    """Complete trust assessment result."""
    overall_score: float
    trust_level: TrustLevel
    overall_pass: bool
    timestamp: datetime
    device_id: str
    categories: List[CategoryScore] = field(default_factory=list)
    check_scores: List[CheckScore] = field(default_factory=list)
    failed_checks: List[CheckScore] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": round(self.overall_score * 100, 1),
            "trust_level": self.trust_level.value,
            "overall_pass": self.overall_pass,
            "timestamp": self.timestamp.isoformat(),
            "device_id": self.device_id,
            "categories": {
                cat.name: {
                    "score": round(cat.category_score * 100, 1),
                    "pass_rate": round(cat.pass_rate * 100, 1),
                    "checks": [
                        {
                            "name": c.check_name,
                            "passed": c.passed,
                            "score": round(c.score * 100, 1),
                            "details": c.details,
                        }
                        for c in cat.checks
                    ],
                }
                for cat in self.categories
            },
            "failed_checks": [
                {"name": c.check_name, "details": c.details, "recommendation": c.recommendation}
                for c in self.failed_checks
            ],
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


class ThresholdConfig:
    """Configuration for scoring thresholds."""

    DEFAULTS = {
        "overall": {
            "pass_threshold": 0.70,  # 70% to pass overall
            "trusted_threshold": 0.80,  # 80%+ for TRUSTED
        },
        "categories": {
            "boot": {"pass_threshold": 0.80, "weight": 2.0},  # Boot security is critical
            "integrity": {"pass_threshold": 0.70, "weight": 2.0},
            "software": {"pass_threshold": 0.60, "weight": 1.0},
            "encryption": {"pass_threshold": 0.70, "weight": 1.5},
            "network": {"pass_threshold": 0.50, "weight": 0.5},
        },
        "critical_checks": [
            "bootloader_lock",
            "verified_boot",
            "selinux_enforcing",
            "file_encryption",
            "screen_lock",
        ],
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULTS.copy()
        if config_path and __import__("os").path.exists(config_path):
            with open(config_path) as f:
                user_config = yaml.safe_load(f) or {}
                self._merge_config(user_config)

    def _merge_config(self, user_config: Dict):
        for section, values in user_config.items():
            if section in self.config:
                self.config[section].update(values)
            else:
                self.config[section] = values

    def get_threshold(self, category: str) -> float:
        cats = self.config.get("categories", {})
        return cats.get(category, {}).get("pass_threshold", 0.5)

    def get_weight(self, category: str) -> float:
        cats = self.config.get("categories", {})
        return cats.get(category, {}).get("weight", 1.0)

    def get_critical_checks(self) -> List[str]:
        return self.config.get("critical_checks", [])

    def get_overall_pass_threshold(self) -> float:
        return self.config.get("overall", {}).get("pass_threshold", 0.7)

    def get_trusted_threshold(self) -> float:
        return self.config.get("overall", {}).get("trusted_threshold", 0.8)


class TrustScorer:
    """
    Main trust scoring engine.
    Aggregates check results and computes overall trust score.
    """

    # Default category weights and descriptions
    CATEGORY_META = {
        "boot": {
            "name": "Boot Security",
            "description": "Bootloader, verified boot, TEE security",
            "weight": 2.0,
        },
        "integrity": {
            "name": "System Integrity",
            "description": "System partition, SELinux, file integrity",
            "weight": 2.0,
        },
        "hardware": {
            "name": "Hardware Security",
            "description": "KeyStore, TEE, hardware attestation",
            "weight": 1.5,
        },
        "software": {
            "name": "Software Security",
            "description": "OS version, security patches, app compatibility",
            "weight": 1.0,
        },
        "encryption": {
            "name": "Data Encryption",
            "description": "File-based encryption, full-disk encryption",
            "weight": 1.5,
        },
        "authentication": {
            "name": "Authentication",
            "description": "Screen lock, biometrics, Secure Unlock",
            "weight": 1.0,
        },
        "network": {
            "name": "Network Security",
            "description": "TLS, certificate validation, network state",
            "weight": 0.5,
        },
    }

    def __init__(self, config: Optional[ThresholdConfig] = None):
        self.config = config or ThresholdConfig()
        self._check_results: List[CheckScore] = []

    def register_check(self, result: CheckScore):
        """Register a check result."""
        self._check_results.append(result)

    def register_check_raw(
        self,
        check_name: str,
        category: str,
        passed: bool,
        details: str = "",
        raw_value: Any = None,
        recommendation: str = "",
        weight: Optional[float] = None,
    ):
        """Register a check result from raw values."""
        # Get default weight from category
        if weight is None:
            weight = self.config.get_weight(category)

        # Compute score
        score = 1.0 if passed else 0.0
        if not passed and recommendation:
            score = 0.1  # Small score for failed with recommendation

        self.register_check(CheckScore(
            check_name=check_name,
            category=category,
            passed=passed,
            score=score,
            weight=weight,
            details=details,
            raw_value=raw_value,
            recommendation=recommendation,
        ))

    def compute_scores(self) -> TrustAssessment:
        """Compute overall trust score from registered checks."""
        # Group by category
        categories: Dict[str, CategoryScore] = {}
        for check in self._check_results:
            if check.category not in categories:
                meta = self.CATEGORY_META.get(check.category, {})
                categories[check.category] = CategoryScore(
                    name=check.category,
                    description=meta.get("description", check.category),
                    weight=meta.get("weight", 1.0),
                )
            categories[check.category].checks.append(check)

        category_scores = list(categories.values())

        # Compute weighted overall score
        total_weight = sum(
            cat.weight * cat.category_score
            for cat in category_scores
        ) / sum(cat.weight for cat in category_scores) if category_scores else 0.0

        # Determine trust level
        if total_weight >= self.config.get_trusted_threshold():
            level = TrustLevel.TRUSTED
        elif total_weight >= 0.6:
            level = TrustLevel.ACCEPTABLE
        elif total_weight >= 0.4:
            level = TrustLevel.CAUTION
        elif total_weight >= 0.2:
            level = TrustLevel.HIGH_RISK
        else:
            level = TrustLevel.UNTRUSTED

        # Check for critical failures
        failed_checks = [c for c in self._check_results if not c.passed]
        critical_names = self.config.get_critical_checks()

        critical_failures = [
            c for c in failed_checks
            if c.check_name in critical_names
        ]

        overall_pass = (
            total_weight >= self.config.get_overall_pass_threshold() and
            len(critical_failures) == 0
        )

        # Generate warnings and recommendations
        warnings = []
        recommendations = []

        for failure in failed_checks:
            if failure.recommendation:
                recommendations.append(failure.recommendation)

        for cat in category_scores:
            cat_threshold = self.config.get_threshold(cat.name)
            if cat.category_score < cat_threshold:
                warnings.append(
                    f"Category '{cat.name}' score ({cat.category_score:.0%}) "
                    f"below threshold ({cat_threshold:.0%})"
                )

        if critical_failures:
            warnings.append(
                f"CRITICAL: {len(critical_failures)} critical check(s) failed — "
                f"{', '.join(c.check_name for c in critical_failures)}"
            )

        return TrustAssessment(
            overall_score=total_weight,
            trust_level=level,
            overall_pass=overall_pass,
            timestamp=datetime.now(),
            device_id="",
            categories=category_scores,
            check_scores=self._check_results,
            failed_checks=failed_checks,
            warnings=warnings,
            recommendations=list(dict.fromkeys(recommendations)),
        )

    def clear(self):
        """Clear all registered check results."""
        self._check_results.clear()

    def run_all_checks(self) -> TrustAssessment:
        """Run all registered check modules and compute final score."""
        assessment = self.compute_scores()
        self.clear()
        return assessment


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Android Trust Scoring Engine")
    parser.add_argument("--config", help="Path to thresholds.yaml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # Demo with sample data
    scorer = TrustScorer(ThresholdConfig(args.config))

    # Register sample checks
    scorer.register_check_raw("bootloader_lock", "boot", True, "Bootloader is locked", weight=2.0)
    scorer.register_check_raw("verified_boot", "boot", True, "Verified boot enabled", weight=2.0)
    scorer.register_check_raw("selinux_enforcing", "integrity", True, "SELinux in enforcing mode", weight=1.5)
    scorer.register_check_raw("file_encryption", "encryption", True, "FBE enabled", weight=1.5)
    scorer.register_check_raw("screen_lock", "authentication", True, "PIN lock enabled", weight=1.0)
    scorer.register_check_raw("security_patch", "software", True, "Security patch 2024-01", weight=1.0)
    scorer.register_check_raw("gms_certified", "software", True, "GMS certified device", weight=1.0)
    scorer.register_check_raw("key_attestation", "hardware", True, "Key attestation supported", weight=1.0)

    result = scorer.compute_scores()

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print("Android Trust Assessment")
        print("=" * 50)
        print(f"Overall Score: {result.overall_score * 100:.1f}/100")
        print(f"Trust Level: {result.trust_level.value.upper()}")
        print(f"Passed: {'✅ YES' if result.overall_pass else '❌ NO'}")
        print()
        print("By Category:")
        for cat in result.categories:
            icon = "✅" if cat.category_score >= 0.7 else "⚠️" if cat.category_score >= 0.4 else "❌"
            print(f"  {icon} {cat.name}: {cat.category_score * 100:.0f}%")
            for check in cat.checks:
                ci = "✅" if check.passed else "❌"
                print(f"    {ci} {check.check_name}")


if __name__ == "__main__":
    main()
