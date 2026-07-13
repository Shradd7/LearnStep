import type { HealthViewState } from "../types/health";

interface BackendHealthCardProps {
  state: HealthViewState;
  onRetry: () => void;
}

export function BackendHealthCard({ state, onRetry }: BackendHealthCardProps) {
  if (state.phase === "loading") {
    return (
      <section className="health-card" aria-live="polite" aria-busy="true">
        <span
          className="status-mark status-mark--checking"
          aria-hidden="true"
        />
        <div>
          <p className="eyebrow">System status</p>
          <h2>Checking the learning service…</h2>
        </div>
      </section>
    );
  }

  if (state.phase === "ready") {
    return (
      <section className="health-card" aria-live="polite">
        <span className="status-mark status-mark--ready" aria-hidden="true" />
        <div>
          <p className="eyebrow">System status</p>
          <h2>Learning service ready</h2>
          <p>
            API, database, and {state.health.embedding_dimension}-dimension
            vector storage are available.
          </p>
        </div>
      </section>
    );
  }

  const detail =
    state.phase === "unavailable"
      ? "The API is responding, but a database or vector-storage readiness check failed."
      : state.message;

  return (
    <section className="health-card health-card--warning" aria-live="assertive">
      <span className="status-mark status-mark--warning" aria-hidden="true" />
      <div>
        <p className="eyebrow">System status</p>
        <h2>Learning service unavailable</h2>
        <p>{detail}</p>
        <button type="button" className="secondary-action" onClick={onRetry}>
          Try again
        </button>
      </div>
    </section>
  );
}
