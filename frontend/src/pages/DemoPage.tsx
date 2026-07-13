import { type FormEvent, useState } from "react";

import {
  getDemoChapters,
  getDemoProgress,
  loginDemo,
  revealDemoHint,
  startDemoSession,
  submitDemoAttempt,
  uploadDemoDocument,
} from "../api/demo";
import type {
  DemoAttempt,
  DemoChapter,
  DemoDocument,
  DemoHint,
  DemoLoginResponse,
  DemoProgress,
  DemoSession,
} from "../types/demo";

const accounts = [
  {
    label: "Class 5 Mathematics",
    email: "math-demo@example.invalid",
    password: "Demo-Math-2026",
  },
  {
    label: "Class 6 Science",
    email: "science-demo@example.invalid",
    password: "Demo-Science-2026",
  },
];

export function DemoPage() {
  const [login, setLogin] = useState<DemoLoginResponse | null>(null);
  const [chapters, setChapters] = useState<DemoChapter[]>([]);
  const [document, setDocument] = useState<DemoDocument | null>(null);
  const [session, setSession] = useState<DemoSession | null>(null);
  const [hints, setHints] = useState<DemoHint[]>([]);
  const [attempt, setAttempt] = useState<DemoAttempt | null>(null);
  const [progress, setProgress] = useState<DemoProgress | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [response, setResponse] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enterDemo(email: string, password: string) {
    setBusy(true);
    setError(null);
    try {
      const authenticated = await loginDemo(email, password);
      const available = await getDemoChapters(authenticated.access_token);
      setLogin(authenticated);
      setChapters(available);
      setDocument(null);
      setSession(null);
      setHints([]);
      setAttempt(null);
      setProgress(null);
    } catch {
      setError(
        "The controlled demo could not start. Check the API and try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!login || !selectedFile) return;
    setBusy(true);
    setError(null);
    try {
      setDocument(
        await uploadDemoDocument(
          login.access_token,
          selectedFile,
          login.profile.class_level,
          login.profile.subject,
        ),
      );
    } catch {
      setError(
        "Upload failed. Use a text-based synthetic PDF under the displayed limits.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function begin(chapter: DemoChapter) {
    if (!login) return;
    setBusy(true);
    setError(null);
    try {
      const matchingDocument = document?.detected_concepts.includes(
        chapter.concept_key,
      )
        ? document.id
        : undefined;
      setSession(
        await startDemoSession(
          login.access_token,
          chapter.package_key,
          matchingDocument,
        ),
      );
      setHints([]);
      setAttempt(null);
      setProgress(null);
      setResponse("");
    } catch {
      setError("The lesson could not be started from the available evidence.");
    } finally {
      setBusy(false);
    }
  }

  async function showHint() {
    if (!login || !session || hints.length >= 2) return;
    setBusy(true);
    try {
      const hint = await revealDemoHint(
        login.access_token,
        session.session_id,
        hints.length + 1,
      );
      setHints((current) => [...current, hint]);
    } catch {
      setError("The next hint could not be shown.");
    } finally {
      setBusy(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!login || !session || !response.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const result = await submitDemoAttempt(
        login.access_token,
        session.session_id,
        response,
      );
      setAttempt(result);
      setProgress(await getDemoProgress(login.access_token));
    } catch {
      setError("Your answer could not be evaluated. Try a shorter response.");
    } finally {
      setBusy(false);
    }
  }

  if (!login) {
    return (
      <main id="main-content" className="demo-page">
        <p className="eyebrow">Controlled portfolio demo</p>
        <h1>Choose a synthetic learner.</h1>
        <p className="demo-intro">
          Do not enter real child information. These accounts and chapters are
          fictional, temporary, and intended only to demonstrate the learning
          flow.
        </p>
        <div className="account-grid">
          {accounts.map((account) => (
            <button
              type="button"
              className="account-card"
              key={account.email}
              disabled={busy}
              onClick={() => void enterDemo(account.email, account.password)}
            >
              <span className="eyebrow">Synthetic account</span>
              <strong>{account.label}</strong>
              <span>Enter demo</span>
            </button>
          ))}
        </div>
        {error && <p className="form-error">{error}</p>}
      </main>
    );
  }

  return (
    <main id="main-content" className="demo-page">
      <header className="demo-heading">
        <div>
          <p className="eyebrow">Upload. Learn. Ace it.</p>
          <h1>{login.account_label}</h1>
        </div>
        <button
          type="button"
          className="secondary-action"
          onClick={() => {
            setLogin(null);
          }}
        >
          Exit demo
        </button>
      </header>
      <div className="notice" role="note">
        <strong>Demonstration content only.</strong>{" "}
        {login.limitations.join(" ")}
      </div>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}

      <section className="demo-section" aria-labelledby="upload-title">
        <p className="eyebrow">Optional upload</p>
        <h2 id="upload-title">Try your own synthetic sample PDF</h2>
        <p>
          Text-based PDF only. The private file receives a generated storage key
          and expires automatically. Never upload real student work here.
        </p>
        <form className="upload-form" onSubmit={(event) => void upload(event)}>
          <label htmlFor="chapter-file">Synthetic chapter PDF</label>
          <input
            id="chapter-file"
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => {
              setSelectedFile(event.target.files?.[0] ?? null);
            }}
          />
          <button type="submit" disabled={!selectedFile || busy}>
            Upload temporarily
          </button>
        </form>
        {document && (
          <div className="evidence-card">
            <strong>{document.display_name}</strong>
            <span>{document.chunk_count} extracted blocks</span>
            <span>
              Concepts:{" "}
              {document.detected_concepts.join(", ") || "needs review"}
            </span>
            <span>
              Expires: {new Date(document.expires_at).toLocaleTimeString()}
            </span>
          </div>
        )}
      </section>

      <section className="demo-section" aria-labelledby="chapters-title">
        <p className="eyebrow">Synthetic chapters</p>
        <h2 id="chapters-title">Choose one learning step</h2>
        <div className="chapter-grid">
          {chapters.map((chapter) => (
            <article key={chapter.package_key} className="chapter-card">
              <span>
                {chapter.subject} · Class {chapter.class_level}
              </span>
              <h3>{chapter.title}</h3>
              <p>{chapter.source.label}</p>
              <p>Confidence: {chapter.confidence.replaceAll("_", " ")}</p>
              <button
                type="button"
                disabled={busy}
                onClick={() => void begin(chapter)}
              >
                Learn this concept
              </button>
            </article>
          ))}
        </div>
      </section>

      {session && (
        <section className="lesson-panel" aria-labelledby="lesson-title">
          <p className="eyebrow">Learn</p>
          <h2 id="lesson-title">{session.title}</h2>
          <dl className="lesson-steps">
            <div>
              <dt>Goal</dt>
              <dd>{session.lesson.goal}</dd>
            </div>
            <div>
              <dt>Prerequisite</dt>
              <dd>{session.lesson.prerequisites}</dd>
            </div>
            <div>
              <dt>Explanation</dt>
              <dd>{session.lesson.explanation}</dd>
            </div>
            <div>
              <dt>Example</dt>
              <dd>{session.lesson.example}</dd>
            </div>
            <div>
              <dt>Recap</dt>
              <dd>{session.lesson.recap}</dd>
            </div>
          </dl>
          <aside className="source-note">
            Source: {session.source.label}, page {session.source.page}. Evidence
            blocks: {session.evidence_chunk_ids.length}. Confidence:{" "}
            {session.confidence.replaceAll("_", " ")}.
          </aside>

          <div className="question-panel">
            <p className="eyebrow">Practise</p>
            <h3>{session.question.text}</h3>
            {session.question.options.length > 0 && (
              <ul>
                {session.question.options.map((option) => (
                  <li key={option}>{option}</li>
                ))}
              </ul>
            )}
            {hints.map((hint) => (
              <p className="hint" key={hint.level}>
                Hint {hint.level}: {hint.hint}
              </p>
            ))}
            {!attempt && hints.length < 2 && (
              <button
                type="button"
                className="secondary-action"
                disabled={busy}
                onClick={() => void showHint()}
              >
                Show hint {hints.length + 1}
              </button>
            )}
            <form
              className="answer-form"
              onSubmit={(event) => void submit(event)}
            >
              <label htmlFor="demo-answer">Your answer</label>
              <input
                id="demo-answer"
                value={response}
                onChange={(event) => {
                  setResponse(event.target.value);
                }}
                disabled={Boolean(attempt)}
              />
              <button
                type="submit"
                disabled={busy || Boolean(attempt) || !response.trim()}
              >
                Check answer
              </button>
            </form>
          </div>
        </section>
      )}

      {attempt && (
        <section className="feedback-panel" aria-labelledby="feedback-title">
          <p className="eyebrow">Feedback · {attempt.confidence} confidence</p>
          <h2 id="feedback-title">{attempt.outcome.replaceAll("_", " ")}</h2>
          <p>{attempt.feedback}</p>
          <p>
            <strong>Explanation:</strong> {attempt.explanation}
          </p>
          <p>
            <strong>Reviewed demo answer:</strong> {attempt.accepted_answer}
          </p>
        </section>
      )}

      {progress && (
        <section className="progress-panel" aria-labelledby="progress-title">
          <p className="eyebrow">Learning evidence</p>
          <h2 id="progress-title">What to do next</h2>
          {progress.observations.map((item) => (
            <article key={item.concept_key}>
              <h3>{item.concept_key.replaceAll("_", " ")}</h3>
              <p>
                {item.attempts_observed} observation recorded;{" "}
                {item.supported_observations} used hints.
              </p>
              <p>{item.next_action}</p>
            </article>
          ))}
          <p className="source-note">{progress.limitation}</p>
        </section>
      )}
    </main>
  );
}
