# Android Trust Anchor — Device Trust Assessment Framework

A comprehensive Android device trust assessment framework that combines
hardware attestation, system integrity checks, and software security
analysis into a unified trust score (0-100) with detailed category breakdowns.

## Features

**15+ Security Checks** across 7 categories:

| Category | Checks |
|---|---|
| **Boot** | Bootloader Lock, DM-Verity, Verified Boot |
| **Integrity** | Root Detection, SELinux, Emulator Detection, Debug Flags |
| **Hardware** | KeyStore, TEE, Hardware Attestation |
| **Encryption** | FBE/FDE, Encryption Status |
| **Authentication** | Screen Lock, Biometric Auth |
| **Software** | Security Patch Level, GMS Certification, Permissions |
| **Network** | ADB Status, USB Config, Network Security |

**Trust Scoring Engine** — `src/scorer.py`
- Weighted scoring by category importance
- Configurable thresholds via YAML
- Critical check enforcement
- Trust level classification: TRUSTED → ACCEPTABLE → CAUTION → HIGH_RISK → UNTRUSTED

**Reporting** — `src/reporter.py`
- HTML report with visual score rings
- JSON structured output
- Text console output

**Configurable** — `config/thresholds.yaml`
- Category weights and pass thresholds
- Scoring curves per check
- Critical check lists

## Quick Start

```bash
# Run full trust assessment
python examples/quick_check.py

# With custom thresholds
python examples/quick_check.py --config config/thresholds.yaml --html report.html

# JSON output
python examples/quick_check.py --json

# Generate HTML report
python -m src.reporter --output trust_report.html
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Trust Assessment Framework               │
│                                                      │
│  ┌──────────────┐    ┌──────────────────────────────┐│
│  │   Checks     │───▶│     TrustScorer Engine      ││
│  │  (15+ mods)  │    │  - Aggregate scores         ││
│  └──────────────┘    │  - Weighted by category     ││
│                      │  - Apply thresholds         ││
│                      └──────────────┬───────────────┘│
│                                       │               │
│                      ┌────────────────▼────────────────┐│
│                      │    TrustAssessment Result       ││
│                      │  - overall_score (0-100)        ││
│                      │  - trust_level (5 levels)       ││
│                      │  - category breakdown           ││
│                      │  - recommendations             ││
│                      └────────────────┬────────────────┘│
│                                       │               │
│                      ┌────────────────▼────────────────┐│
│                      │   ReportGenerator              ││
│                      │   HTML | JSON | Text           ││
│                      └───────────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

## Trust Levels

| Level | Score | Meaning |
|---|---|---|
| **TRUSTED** | 80-100 | Fully trusted, no concerns |
| **ACCEPTABLE** | 60-79 | Generally acceptable with minor issues |
| **CAUTION** | 40-59 | Proceed with care, investigate issues |
| **HIGH_RISK** | 20-39 | Significant security concerns |
| **UNTRUSTED** | 0-19 | Do not trust for sensitive operations |

## Scoring Weights (Default)

| Category | Weight | Pass Threshold |
|---|---|---|
| Boot | 2.0 | 80% |
| Integrity | 2.0 | 70% |
| Hardware | 1.5 | 70% |
| Encryption | 1.5 | 70% |
| Authentication | 1.0 | 60% |
| Software | 1.0 | 60% |
| Network | 0.5 | 50% |

## Critical Checks (Must Pass)

These checks must pass for the overall assessment to pass:
- `bootloader_lock` — Bootloader must be locked
- `verified_boot` — Verified boot must be enabled
- `selinux_enforcing` — SELinux must be enforcing
- `device_encryption` — Device must be encrypted
- `screen_lock` — Screen lock must be configured
- `root_detection` — Device must not be rooted
- `emulator_detection` — Must not be an emulator

## Contact & Support

- **Website:** [qtphone.com](https://qtphone.com)
- **GitHub Issues:** Open an issue in this repository
- **Email:** contact@qtphone.com

## License

MIT License
