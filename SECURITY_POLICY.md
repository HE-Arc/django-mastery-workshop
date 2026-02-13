# Security Policy

Last Updated: February 13, 2026

## Scope

This document outlines the software security measures applied to the `django-exemple` project (Newspaper API), with a policy style aligned with the EU Cyber Resilience Act (CRA) expectations.

## Dependency Management

- All Python runtime dependencies are pinned in `requirements.txt`.
- A Software Bill of Materials (SBOM) is generated in CycloneDX JSON format (`sbom.json`).
- Vulnerability audits are run with `pip-audit`.

## How To Run Security Checks

### 1. Vulnerability Audit (local)

```bash
pip-audit -r requirements.txt > audit-report.txt
```

### 2. Vulnerability Audit (Docker)

```bash
docker compose exec web pip-audit -r requirements.txt > audit-report.txt
```

### 3. Generate SBOM (CycloneDX JSON)

```bash
cyclonedx-py requirements --output-file sbom.json --output-format json
```

## Latest Security Audit

- Date: February 13, 2026
- Tool: `pip-audit`
- Result: No known vulnerabilities found
- SBOM generated: `sbom.json`

## Audit Frequency

- After each dependency update
- Before every major release
- In CI on pull requests (recommended)

## Vulnerability Response Policy

- An audit report (`audit-report.txt`) is retained.
- Internal impact analysis is performed for each finding.
- Critical vulnerability target SLA: mitigation or patch within 72 hours.

