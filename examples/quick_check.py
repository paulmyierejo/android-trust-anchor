"""
Quick Trust Check Example
Demonstrates running a complete device trust assessment.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scorer import TrustScorer, ThresholdConfig
from src.reporter import TrustReportGenerator


def run_assessment(config_path: str = None):
    """Run a complete trust assessment with all available checks."""
    config = ThresholdConfig(config_path)
    scorer = TrustScorer(config)

    # Import all check modules
    from src.checks import (
        BootloaderCheck, RootCheck, SELinuxCheck, EncryptionCheck,
        ScreenLockCheck, EmulatorCheck, IntegrityCheck, OTACheck,
        ADBCheck, USBCheck, DebugCheck, VerityCheck,
        BiometricCheck, NetworkCheck, PermissionCheck,
    )

    # Run all checks
    check_classes = [
        BootloaderCheck, RootCheck, SELinuxCheck, EncryptionCheck,
        ScreenLockCheck, EmulatorCheck, IntegrityCheck, OTACheck,
        ADBCheck, USBCheck, DebugCheck, VerityCheck,
        BiometricCheck, NetworkCheck, PermissionCheck,
    ]

    print("Running trust checks...")
    for cls in check_classes:
        try:
            result = cls.run()
            scorer.register_check(result)
            icon = "✅" if result.passed else "❌"
            print(f"  {icon} {result.check_name}: {result.score:.0%} ({result.details})")
        except Exception as e:
            print(f"  ⚠️  {cls.__name__}: Error - {e}")

    # Compute final assessment
    print("\nComputing trust scores...")
    assessment = scorer.compute_scores()

    # Print summary
    print(f"\nOverall Score: {assessment.overall_score * 100:.1f}/100")
    print(f"Trust Level:   {assessment.trust_level.value.upper()}")
    print(f"Overall Pass:  {'YES ✅' if assessment.overall_pass else 'NO ❌'}")

    print("\nBy Category:")
    for cat in assessment.categories:
        cat_pct = cat.category_score * 100
        icon = "✅" if cat.category_score >= 0.7 else "⚠️" if cat.category_score >= 0.4 else "❌"
        print(f"  {icon} {cat.name}: {cat_pct:.0f}%")

    if assessment.recommendations:
        print("\nRecommendations:")
        for rec in assessment.recommendations:
            print(f"  ⚠️  {rec}")

    return assessment


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quick Trust Assessment")
    parser.add_argument("--config", help="Path to thresholds.yaml")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--html", help="Output HTML path")
    args = parser.parse_args()

    assessment = run_assessment(args.config)

    if args.json:
        print(json.dumps(assessment.to_dict(), indent=2, default=str))

    if args.html:
        generator = TrustReportGenerator()
        generator.save_report(assessment, args.html, "html")
        print(f"\nHTML report saved to: {args.html}")
