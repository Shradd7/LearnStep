# LearnStep architecture

LearnStep is a modular monolith: one React browser application, one FastAPI process, one PostgreSQL/pgvector database, and private file storage. It does not require an external LLM.

## Request flow

1. A user selects one of two synthetic demo identities.
2. FastAPI verifies the Argon2 password hash and returns a short-lived signed demo token.
3. An optional PDF upload is validated as untrusted input and stored under a generated key outside the web root.
4. PyMuPDF preserves page text; deterministic rules label content blocks and map only known synthetic concept aliases.
5. Chunks retain owner, document, class, subject, concept, content type, page, text hash, embedding version, and vector.
6. Retrieval requires all ownership and learning-context filters before cosine ordering.
7. A deterministic package builds goal → prerequisite → explanation → example → question → recap → source.
8. Hints are revealed in sequence. The answer is returned only after an attempt.
9. Answer-type rules produce transparent features and immutable attempt observations.
10. Progress reports counts and next actions, never rankings, labels, or invented mastery percentages.

## Retention and deletion

Demo uploads expire after 60 minutes by default. A background cleanup loop and document endpoints purge expired database records and private files. Explicit deletion checks ownership, deletes the file, and cascades derived chunks. Production object storage must also enforce an independent lifecycle rule.

## Current embedding boundary

The configured reviewed-content contract remains 384 dimensions for `all-MiniLM-L6-v2`, but the controlled upload/retrieval demo uses a clearly labeled deterministic 384-dimensional hash vector. This keeps local evaluation reproducible without downloading a model and must not be represented as semantic embedding quality.
