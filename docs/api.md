# LearnStep API

Interactive OpenAPI documentation is available at `/docs`. All product routes are under `/api/v1`; health routes remain unversioned.

## Health

- `GET /health/live`
- `GET /health/ready` — checks PostgreSQL, pgvector, and vector dimension.

## Controlled demo

- `POST /api/v1/demo/login` — accepts only bundled synthetic account credentials.
- `GET /api/v1/demo/chapters` — returns packages matching the authenticated profile.
- `POST /api/v1/documents` — multipart PDF upload with `class_level` and `subject`.
- `GET /api/v1/documents` — lists active owner-scoped temporary documents.
- `DELETE /api/v1/documents/{id}` — deletes owner-scoped file and derived chunks.
- `POST /api/v1/retrieval/search` — requires document IDs, class, subject, concepts, query, and limit.
- `POST /api/v1/demo/sessions` — starts a deterministic package, optionally grounded in an owned upload.
- `POST /api/v1/demo/sessions/{id}/hints/{level}` — reveals hint 1 then hint 2.
- `POST /api/v1/demo/sessions/{id}/attempts` — evaluates MCQ or numeric response and then reveals answer/explanation.
- `GET /api/v1/demo/progress` — returns evidence counts and next actions, not mastery percentages.

Bearer tokens are held in frontend memory and expire. The demo API is not a production authentication system. FastAPI validation errors currently use the framework error shape; a uniform request-ID error envelope remains production work.
