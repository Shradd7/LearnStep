# ADR-0001: Governing product scope

- Status: accepted; source-document correction pending
- Date: 2026-07-13

`AGENTS.md`, `CODEX_INSTRUCTIONS.md`, and the user's current direction define a Classes 5–8 Mathematics and Science learning companion. `PRD.md` describes a different ResumeLens interview coach.

The documented priority is latest user instruction, `AGENTS.md`, PRD safety constraints, then implementation guidance. LearnStep therefore follows the learning-companion scope and does not import résumé, target-role, hiring, or interview features. The conflicting PRD remains visible and must be corrected by the repository owner.

The product-facing name is LearnStep with the tagline “Upload. Learn. Ace it.” The internal Python import namespace remains `classpath` to avoid a risky package and migration rewrite.
