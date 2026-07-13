# Threat model

## Protected assets

Temporary PDF bytes, extracted text, owner-scoped chunks and embeddings, signed demo sessions, attempts, and database credentials.

## Implemented controls

- PDF extension, MIME, `%PDF` bytes, maximum bytes/pages, encryption, parser failure, and extractable-text threshold checks.
- Filenames are reduced to a safe display basename; storage uses server-generated keys outside public paths.
- PDF text is processed as data only. Links, scripts, attachments, forms, macros, and embedded instructions are never executed.
- Argon2 password hashes and short-lived HMAC-signed tokens for synthetic accounts.
- Retrieval query functions require authenticated `user_id`, explicit document IDs, class, subject, and concept filters.
- Cross-user API and real-pgvector regression tests.
- Explicit and expiry-based deletion of files and derived records.
- Explicit CORS allowlist and production rejection of the development token secret.
- ORM-parameterized queries and validated Pydantic boundaries.

## Residual threats

- No distributed rate limiter or managed WAF is configured.
- The demo token flow is not a complete production account/consent system.
- Local private storage has no provider-managed encryption key or independent lifecycle policy.
- Dependency/image scanning, CSP/secure headers, audit-log review, backup/restore, alerting, and incident response are incomplete.
- The deterministic hash vector is unsuitable for confidential production retrieval quality.
- Content correctness is not human-reviewed; unsafe or misleading uploaded text may be displayed as attributed evidence.

Prompt injection in a PDF has no command channel because the system has no LLM or tool-executing agent. It remains an untrusted-content/display risk.
