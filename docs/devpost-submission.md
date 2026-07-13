# LearnStep Devpost submission package

This file contains copy-ready submission text for the controlled synthetic demo. It does not describe a public child-facing deployment.

## Project name

LearnStep

## Tagline

Upload. Learn. Ace it. 🚀

## Repository

<https://github.com/Shradd7/LearnStep>

## Try it out

<https://github.com/Shradd7/LearnStep>

Use this repository/evidence URL because the executable application is currently a local controlled demo. There is no public live-app URL.

## Inspiration

Students often struggle not because they cannot learn, but because an explanation is too advanced, too generic, or disconnected from their own chapter. We wanted a study buddy that adapts to a learner's class, subject, and material without turning learning into another generic worksheet or competitive score.

## What it does

LearnStep is an NLP-first learning companion demonstration for Classes 5–8 Mathematics and Science. A synthetic learner can choose a chapter or temporarily upload a text-based synthetic PDF. LearnStep preserves page evidence, detects educational content types and known synthetic concepts, retrieves owner-scoped evidence, and presents a deterministic teaching sequence: goal, prerequisite, explanation, example, practice question, staged hints, answer feedback, recap, and revision evidence.

Instead of calling learners “weak” or “smart,” the interface records observations and next actions. Demo uploads are privately stored under generated keys, expire automatically, and can be deleted with their derived records.

## How we built it

The project is a modular monolith with a React/TypeScript frontend, FastAPI/Pydantic backend, PostgreSQL 16 with pgvector, Alembic migrations, private temporary file storage, PyMuPDF extraction, deterministic educational NLP rules, scoped vector retrieval, and answer-type-specific evaluators. Docker Compose runs the full local stack. The v1 demo has no external LLM.

Codex and GPT-5.6 supported planning, implementation, testing, auditing, documentation, safety-boundary iteration, and synthetic evaluation packaging. Claims were limited to executable checks and committed artifacts; Codex output was not counted as human curriculum review.

## Challenges

- Keeping the experience useful without letting a generative model invent educational content.
- Enforcing ownership and class/subject/concept filters before vector similarity search.
- Preserving a hint-first teaching flow while keeping answer evaluation transparent.
- Reporting perfect generator-controlled scores honestly without presenting them as real-world performance.
- Separating learning observations from ranking, ability labels, or unsupported mastery percentages.

## Accomplishments

- A complete synthetic local journey from learner entry through lesson, hint, feedback, progress, and deletion.
- Real PostgreSQL/pgvector integration tests with zero cross-user retrieval in the 120-query synthetic evaluation.
- Secure temporary PDF validation, generated storage keys, expiry cleanup, and derived-record deletion.
- Reproducible synthetic extraction, TF-IDF baseline, retrieval/isolation, and MCQ/numeric evaluator reports.
- Six verified 3:2 screenshots and a 63-second silent captioned demo video.

## What we learned

RAG quality is not just an embedding score: ownership and curriculum metadata filters are essential safety boundaries. Synthetic fixtures are valuable for deterministic regression testing, but even perfect scores do not establish educational validity. A simpler baseline should remain the default until a licensed, human-reviewed dataset justifies DistilBERT.

## What's next

Complete qualified review of 100 lesson/question packages; create an approved, human-reviewed classifier dataset; compare DistilBERT against TF-IDF on a frozen grouped test set; expand legally permitted document-layout evaluation; and rehearse monitoring, deletion, backup, and restore controls before any controlled public deployment. A real child-facing release would additionally require qualified privacy/legal and educational review. No educational-improvement claim should be made without a properly designed student study.

## Measured synthetic results

| Evaluation | Result |
| --- | --- |
| Extraction | 60/60 generator-controlled PDFs extracted; content-type and concept micro F1 1.00 |
| Cognitive classifier | Majority macro F1 0.0556; synthetic TF-IDF macro F1 1.00 on grouped test n=64 |
| Difficulty classifier | Majority macro F1 0.1818; synthetic TF-IDF macro F1 1.00 on grouped test n=64 |
| Retrieval | Recall@5 1.00; MRR@10 1.00; zero cross-user/wrong-class/wrong-concept results across 120 synthetic queries |
| Assessment | 1.00 rule-outcome accuracy on 100 MCQ and 100 numeric synthetic cases |

All results are generator-controlled synthetic software evidence. DistilBERT was not run, no human review is claimed, and no student study exists.

## Media

- `docs/media/devpost/01-landing.png` — product boundary and landing page
- `docs/media/devpost/02-synthetic-learner-selection.png` — synthetic class/subject selection
- `docs/media/devpost/03-chapter-selection.png` — synthetic chapter/source/confidence selection
- `docs/media/devpost/04-source-grounded-lesson.png` — structured lesson and source details
- `docs/media/devpost/05-staged-hint.png` — hint-first practice state
- `docs/media/devpost/06-feedback-and-progress.png` — deterministic feedback and non-ranking evidence
- `docs/media/devpost/learnstep-demo.mp4` — silent captioned demo, 63.20 seconds, 1440×960 H.264, no audio

No authenticated video-upload integration is configured, so there is no public video-platform URL. Upload `learnstep-demo.mp4` to YouTube as **Unlisted**, then paste the resulting `https://youtu.be/...` URL into Devpost.

## Codex `/feedback` session

`019f5bf0-0299-7a62-ad99-1e6e0c5858e2`

The value was read from the local Codex Desktop `session_meta` record for this repository; it was not reconstructed or guessed.

## Submission checklist

Completed:

- [x] Public GitHub repository exists.
- [x] README contains architecture, setup, synthetic credentials, measured results, limitations, screenshots, video, and Codex/GPT-5.6 disclosure.
- [x] Six meaningful PNG screenshots are 1440×960 and below 5 MB.
- [x] Silent captioned MP4 is 63.20 seconds, 1440×960 H.264, and contains no audio stream.
- [x] Synthetic evaluation artifacts, dataset/model cards, privacy boundary, threat model, API docs, Docker setup, and deployment design are present.
- [x] Exact Codex `/feedback` session ID was verified from local session metadata.

Local-only or externally blocked:

- [ ] No public live application URL; localhost is not submitted as public.
- [ ] No public video-platform URL; manual authenticated upload is required.
- [ ] No Azure deployment; cost, subscription, region, credentials, and hostname approval are absent.
- [ ] Human package review remains 0/100.
- [ ] DistilBERT training and real-school validation are not complete.
- [ ] No child-facing launch or educational-improvement claim.
