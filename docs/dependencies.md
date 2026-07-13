# Dependency rationale

Dependencies use bounded compatible ranges and have a direct current purpose.

| Dependency | Direct purpose | License family | Maintenance rationale |
| --- | --- | --- | --- |
| FastAPI, Pydantic, pydantic-settings, Uvicorn | typed API and validated configuration | MIT/BSD | mature, actively maintained Python API stack |
| SQLAlchemy, Alembic, psycopg | PostgreSQL persistence and migrations | MIT | established PostgreSQL workflow with Python 3.12 support |
| pgvector Python + PostgreSQL extension | typed vector column and dimension checks | MIT/PostgreSQL | standard pgvector integration; no separate vector service |
| PyMuPDF | validate and extract page-preserving text from PDFs | AGPL/commercial dual license | maintained parser selected by the repository specification; distribution obligations require review |
| Argon2-cffi, PyJWT | established password hashing and signed short-lived demo tokens | MIT | avoids custom password cryptography and keeps the demo auth boundary explicit |
| python-multipart | bounded FastAPI file upload parsing | Apache-2.0 | direct requirement for multipart PDF endpoints |
| scikit-learn (evaluation extra) | majority and TF-IDF Logistic Regression baselines | BSD-3-Clause | required simpler baseline before any transformer experiment; excluded from runtime image |
| pytest, httpx, Ruff, mypy | deterministic tests, lint/format, strict typing | MIT | focused development-only tooling |
| React, React DOM, React Router | accessible routed application shell | MIT | maintained SPA foundation without a UI framework |
| Vite, TypeScript | strict compilation and production build | MIT/Apache-2.0 | small modern frontend toolchain |
| Vitest, Testing Library, jsdom | user-visible component state tests | MIT | Vite-aligned deterministic local tests |
| ESLint, typescript-eslint, Prettier | lint and formatting contracts | MIT | maintained TypeScript quality tooling |
| Nginx | serve built static frontend in Compose | BSD-2-Clause | small stable runtime; no Node development server in runtime image |

License entries are engineering metadata, not legal advice. Transitive dependencies must be reviewed before production distribution.
