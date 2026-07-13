# Controlled deployment design — Azure Container Apps

No cloud resources or public URL have been created. This is the single documented target path, not a completed deployment.

`.github/workflows/deploy-azure.yml` provides a manual OIDC-based build, push, migration-job, revision-update, and readiness sequence. It is intentionally inert until the `portfolio-demo` GitHub environment, Azure workload identity, registry, apps, database, private storage, and migration job are provisioned and approved.

## Intended topology

```text
Public HTTPS
  ├─ static LearnStep frontend container (Nginx)
  └─ private-ingress FastAPI container where platform routing permits
        ├─ Azure Database for PostgreSQL Flexible Server + pgvector
        ├─ private Azure Blob container for temporary PDFs
        ├─ Key Vault references for secrets
        └─ Application Insights / Log Analytics with privacy-safe fields
```

Use Azure Container Registry and Azure Container Apps revisions. Run Alembic as an explicit release job before shifting traffic; never from every web worker. Blob lifecycle rules must delete demo uploads after the approved short retention and provide a backstop for application deletion. Database backups, point-in-time restore, migration rollback, and document-deletion reconciliation must be rehearsed in staging.

## Required production controls

- a generated `DEMO_TOKEN_SECRET`, HTTPS-only origin allowlist, secure headers, request/upload rate limits, and non-public database networking;
- managed PostgreSQL with verified pgvector support and restricted credentials;
- private Blob storage with encryption, generated keys, no anonymous access, and lifecycle deletion;
- structured logs containing request ID, route, status, duration, and version only—never PDF text, answers, tokens, embeddings, or personal filenames;
- health/readiness, latency/error/deletion alerts, container/image scanning, backup/restore and rollback runbooks;
- a visible demo-only notice and no registration or real-child-data request.

## Release gate

Provisioning may create cost and requires the user to choose an Azure subscription/resource region, approve spend, provide deployment credentials, and approve the public hostname. GitHub Actions secrets would then be needed for registry and Azure workload identity. Until those choices exist, the repository can build deployable containers but cannot honestly claim a deployment or URL.
