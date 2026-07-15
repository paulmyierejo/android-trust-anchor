"""
Trust Assessment Reporter
Generates HTML, JSON, and console reports from trust assessment results.
"""

import json
from typing import Dict, Any
from datetime import datetime
from .scorer import TrustAssessment, TrustLevel


class TrustReportGenerator:
    """Generates reports from trust assessment results."""

    @staticmethod
    def generate_html(assessment: TrustAssessment, title: str = "Android Trust Report") -> str:
        """Generate an HTML report."""
        score_pct = assessment.overall_score * 100
        level = assessment.trust_level.value.upper()
        level_color = {
            "TRUSTED": "#4CAF50",
            "ACCEPTABLE": "#8BC34A",
            "CAUTION": "#FFC107",
            "HIGH_RISK": "#FF9800",
            "UNTRUSTED": "#f44336",
        }.get(level, "#9E9E9E")

        checks_by_cat = {}
        for cat in assessment.categories:
            checks_by_cat[cat.name] = {
                "score": cat.category_score,
                "checks": cat.checks,
            }

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8f9fa; color: #333; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 22px; margin-bottom: 4px; }}
        .score-card {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; text-align: center; }}
        .score-circle {{ width: 140px; height: 140px; border-radius: 50%; background: conic-gradient({level_color} {score_pct}%, #e0e0e0 0); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }}
        .score-inner {{ width: 110px; height: 110px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; flex-direction: column; }}
        .score-number {{ font-size: 32px; font-weight: bold; color: {level_color}; }}
        .score-label {{ font-size: 12px; color: #666; }}
        .level-badge {{ display: inline-block; padding: 6px 20px; border-radius: 20px; font-size: 14px; font-weight: bold; color: white; background: {level_color}; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h2 {{ font-size: 14px; color: #666; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .cat-row {{ display: flex; align-items: center; margin-bottom: 14px; }}
        .cat-name {{ width: 160px; font-size: 13px; font-weight: 500; }}
        .cat-bar-wrap {{ flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; margin: 0 12px; overflow: hidden; }}
        .cat-bar {{ height: 100%; border-radius: 4px; background: {level_color}; transition: width 0.5s ease; }}
        .cat-score {{ width: 40px; font-size: 13px; font-weight: bold; color: #333; text-align: right; }}
        .check-list {{ margin-top: 8px; }}
        .check-item {{ display: flex; align-items: center; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }}
        .check-item:last-child {{ border-bottom: none; }}
        .check-icon {{ width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 11px; }}
        .icon-pass {{ background: #e8f5e9; color: #4CAF50; }}
        .icon-fail {{ background: #ffebee; color: #f44336; }}
        .recommendation {{ background: #fff8e1; border-left: 4px solid #FFC107; padding: 12px 16px; border-radius: 4px; margin-top: 8px; font-size: 13px; }}
        .recommendation li {{ margin: 4px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
        @media (max-width: 600px) {{ .cat-name {{ width: 110px; font-size: 12px; }} }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Android Device Trust Assessment</h1>
        <div style="opacity:0.8; font-size:13px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>

    <div class="score-card">
        <div class="score-circle">
            <div class="score-inner">
                <div class="score-number">{score_pct:.0f}</div>
                <div class="score-label">/ 100</div>
            </div>
        </div>
        <div class="level-badge">{level}</div>
        <div style="margin-top:12px; color:#666; font-size:13px;">
            Overall: {'PASS ✅' if assessment.overall_pass else 'FAIL ❌'}
        </div>
    </div>
"""

        # Category breakdown
        html += '<div class="card">\n<h2>Category Scores</h2>\n'
        for cat in assessment.categories:
            cat_pct = cat.category_score * 100
            html += f'''
        <div class="cat-row">
            <div class="cat-name">{cat.name.capitalize()}</div>
            <div class="cat-bar-wrap"><div class="cat-bar" style="width:{cat_pct}%"></div></div>
            <div class="cat-score">{cat_pct:.0f}%</div>
        </div>
        <div class="check-list">
'''
            for check in cat.checks:
                icon_class = "icon-pass" if check.passed else "icon-fail"
                icon_char = "✓" if check.passed else "✗"
                html += f'''
            <div class="check-item">
                <div class="check-icon {icon_class}">{icon_char}</div>
                <span>{check.check_name}</span>
                <span style="margin-left:auto; color:#999; font-size:12px;">{check.details}</span>
            </div>
'''
            html += '</div>\n'

        html += '</div>\n'

        # Failed checks & recommendations
        if assessment.recommendations:
            html += '<div class="card">\n<h2>Recommendations</h2>\n<ul class="recommendation">\n'
            for rec in assessment.recommendations:
                html += f'<li>⚠️  {rec}</li>\n'
            html += '</ul>\n</div>\n'

        # Warnings
        if assessment.warnings:
            html += '<div class="card">\n<h2>Warnings</h2>\n<ul style="color:#d32f2f; font-size:13px;">\n'
            for warn in assessment.warnings:
                html += f'<li>⚠️  {warn}</li>\n'
            html += '</ul>\n</div>\n'

        html += f'''
    <div class="footer">
        Trust Assessment Report | Generated by Android Trust Anchor | qtphone.com
    </div>
</div>
</body>
</html>
'''
        return html

    @staticmethod
    def generate_json(assessment: TrustAssessment) -> str:
        return json.dumps(assessment.to_dict(), indent=2, default=str)

    @staticmethod
    def generate_text(assessment: TrustAssessment) -> str:
        score_pct = assessment.overall_score * 100
        lines = [
            "=" * 55,
            "  Android Device Trust Assessment",
            "=" * 55,
            f"Overall Score:  {score_pct:.1f} / 100",
            f"Trust Level:    {assessment.trust_level.value.upper()}",
            f"Overall:        {'PASS ✅' if assessment.overall_pass else 'FAIL ❌'}",
            "-" * 55,
            "Category Scores:",
        ]

        for cat in assessment.categories:
            cat_pct = cat.category_score * 100
            icon = "✅" if cat.category_score >= 0.7 else "⚠️" if cat.category_score >= 0.4 else "❌"
            lines.append(f"  {icon} {cat.name.capitalize():<15} {cat_pct:>6.1f}%")

        lines.extend(["", "Check Results:"])
        for cat in assessment.categories:
            for check in cat.checks:
                icon = "✅" if check.passed else "❌"
                lines.append(f"  {icon} {check.check_name}")

        if assessment.recommendations:
            lines.extend(["", "Recommendations:"])
            for rec in assessment.recommendations:
                lines.append(f"  ⚠️  {rec}")

        lines.extend(["", "=" * 55])
        return "\n".join(lines)

    def save_report(
        self,
        assessment: TrustAssessment,
        output_path: str,
        format: str = "html",
    ):
        """Save report to file."""
        if format == "html":
            content = self.generate_html(assessment)
        elif format == "json":
            content = self.generate_json(assessment)
        else:
            content = self.generate_text(assessment)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    import argparse
    from .scorer import TrustScorer

    parser = argparse.ArgumentParser(description="Android Trust Report Generator")
    parser.add_argument("--output", default="trust_report.html")
    parser.add_argument("--format", choices=["html", "json", "text"], default="html")
    args = parser.parse_args()

    # Run a demo assessment
    scorer = TrustScorer()
    from .checks import (
        BootloaderCheck, RootCheck, SELinuxCheck, EncryptionCheck,
        ScreenLockCheck, EmulatorCheck, IntegrityCheck, OTACheck,
        ADBCheck, USBCheck, DebugCheck, VerityCheck,
        BiometricCheck, NetworkCheck, PermissionCheck,
    )

    check_classes = [
        BootloaderCheck, RootCheck, SELinuxCheck, EncryptionCheck,
        ScreenLockCheck, EmulatorCheck, IntegrityCheck, OTACheck,
        ADBCheck, USBCheck, DebugCheck, VerityCheck,
        BiometricCheck, NetworkCheck, PermissionCheck,
    ]

    for cls in check_classes:
        try:
            result = cls.run()
            scorer.register_check(result)
        except Exception as e:
            pass

    assessment = scorer.compute_scores()

    generator = TrustReportGenerator()
    generator.save_report(assessment, args.output, args.format)
    print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()
