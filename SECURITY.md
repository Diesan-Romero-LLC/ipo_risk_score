# Security Policy

This document describes how security is handled in the **IPO Risk Score** project and how to report potential vulnerabilities or security-sensitive issues.

The project is a **research-oriented Python library** that implements a logistic-bounded risk scoring model for IPOs. It is **not** an authentication system, web framework, or infrastructure component; however, we still treat input validation, dependency hygiene, and responsible disclosure seriously.

---

## Supported Versions

Security-related fixes are applied to:

- The `main` branch (development and latest features)
- The latest tagged release (if applicable)

Older releases may not receive backported security patches. If you are using an older version in a security-sensitive environment, you are strongly encouraged to upgrade to the latest release.

---

## Reporting a Vulnerability

If you believe you have found a security issue, **do not open a public GitHub issue** describing it in detail.

Instead, please report it privately:

- **Email:** `me@diesanromero.com`
- **Subject line suggestion:** `IPO Risk Score – Security Issue`

When reporting:

1. Provide a **clear description** of the issue.
2. Include **steps to reproduce** if possible (code snippet, inputs, etc.).
3. Indicate any **potential impact** you foresee (e.g., model misuse, denial of service, information leakage).
4. If relevant, mention your **environment** (Python version, OS, deployment context).

You will receive an acknowledgment as soon as reasonably possible, and we will work with you on:

- Understanding the issue.
- Validating its impact and scope.
- Implementing a fix.
- Coordinating a responsible disclosure timeline, if applicable.

---

## Scope

This project’s security surface is mainly:

1. **Input handling and validation**
   - The `IpoInput` structure and domain entities.
   - Feature engineering logic under `domain/risk/features/`.
   - Validation logic under `domain/risk/validators.py`.
   - Logistic scoring under `domain/risk/logistic.py`.

2. **Dependency and tooling safety**
   - Python dependencies installed via `pyproject.toml`.
   - Development tools (`pytest`, `ruff`, `black`, `mypy`, etc.).

3. **Examples and sample code**
   - Scripts under `examples/` which demonstrate how to use the library.

The project does **not** include:

- Network listeners or web servers by default.
- Credential storage or user authentication.
- Database connectors or direct data persistence.

If you are integrating `ipo-risk-score` into a web service, API, or production pipeline, **the security of that surrounding system is out of scope for this repository**, but you should still follow the “Safe Usage Guidelines” below.

---

## How We Handle Security Issues

When a security issue is reported:

1. **Triage**
   - Confirm whether the report is valid and within scope.
   - Determine severity and potential impact.

2. **Fix**
   - Implement a patch in a private or restricted branch, if needed.
   - Extend or add tests (e.g., validation and boundary tests) to prevent regressions.
   - Ensure the fix respects the model’s domain semantics and the original paper.

3. **Release**
   - Publish a new patch/minor release if appropriate.
   - Update documentation (README, SECURITY.md, or other docs) if behavior changes.
   - Optionally publish a short security advisory in the repository’s releases or issues.

4. **Disclosure**
   - Coordinate timing and content with the reporter when relevant.
   - Avoid disclosing exploit details until a fix is available and users have had a reasonable time window to upgrade.

---

## Input Validation & Model Safety

The library is designed with **defensive input validation**:

- IPO inputs are validated via `validate_ipo_input` before scoring:
  - Numeric fields must be finite (no NaN or infinity).
  - Prices and shares must be positive and within reasonable upper bounds.
  - Free float must be in `[0, 100]`.
  - Lock-up days must be non-negative.
  - Revenue, margins, and growth must fall into domain-informed ranges.
  - Categorical fields (e.g., `underwriter_tier`, `sector_cyclicality`, `region_risk_tier`) must belong to allowed sets.
- Strings such as `ticker`, `company_name`, `country`, and `sector`:
  - Have length limits.
  - Are checked for control characters.
  - Follow a conservative pattern for `ticker` (e.g., `[A-Z0-9.\-]+`).

The logistic scoring function:

- Validates feature values for finiteness and safe bounds.
- Uses a **clipped logistic transform** to avoid numerical overflows.
- Ensures the returned risk score lies within `[0, 100]`.

If you identify an input or feature combination that bypasses these protections or yields unstable behavior, please report it as described above.

---

## Safe Usage Guidelines

If you use **IPO Risk Score** in your own applications, especially in production or client-facing contexts:

1. **Do not trust unvalidated user input**
   - Always enforce your own input validation layer (e.g., via Pydantic in FastAPI, JSON schema, etc.).
   - Limit payload sizes, enforce types, and treat all external data as untrusted.

2. **Avoid embedding sensitive data in fields**
   - `ticker`, `company_name`, `country`, and `sector` are meant for identifiers and classification, not for free-form logs, secrets, or PII.
   - Do not place credentials, API keys, or personal information in these strings.

3. **Dependency hygiene**
   - Use pinned or constrained dependency versions when embedding this library into a larger system.
   - Regularly run dependency vulnerability scanners (`pip-audit`, `safety`, etc.).

4. **Logging**
   - Be mindful of what you log: risk scores are not secrets, but input data might be sensitive in some environments.
   - Redact or anonymize data where required by your security/privacy policies.

5. **Model governance**
   - Remember that this is a **research-oriented model**. Final decisions (investment, compliance, risk approvals) should not rely exclusively on this score.
   - Document any internal policies on how the score is interpreted and combined with other signals.

---

## Out of Scope

The following are **out of scope** for this repository’s security policy:

- Vulnerabilities arising solely from misconfiguration of external systems (servers, containers, CI/CD, etc.).
- Issues in third-party components unrelated to this project and its direct dependencies.
- Ethical or regulatory questions around how model outputs are used (e.g., investment decisions, suitability for a given investor).

Those topics are important, but they must be handled at the organizational level.

---

If you have any doubts about whether an issue is in scope or how to report something, please err on the side of caution and contact us privately at `me@diesanromero.com`.
