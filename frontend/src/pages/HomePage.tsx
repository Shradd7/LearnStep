import { BackendHealthCard } from "../components/BackendHealthCard";
import { useBackendHealth } from "../features/health/useBackendHealth";

export function HomePage() {
  const { state, retry } = useBackendHealth();

  return (
    <main id="main-content">
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Upload. Learn. Ace it.</p>
        <h1 id="hero-title">Your chapter, one clear step at a time.</h1>
        <p className="hero__intro">
          LearnStep is an NLP-first learning companion for Classes 5–8
          Mathematics and Science. It turns uploaded learning material into
          short, grounded lessons, class-appropriate questions, staged hints,
          feedback, and revision evidence.
        </p>
        <div className="notice" role="note">
          <strong>Synthetic development content only.</strong> No demo topic
          shown by this build is reviewed curriculum or an official board
          mapping.
        </div>
      </section>
      <BackendHealthCard state={state} onRetry={retry} />
      <section className="principles" aria-labelledby="principles-title">
        <p className="eyebrow">Built in from the start</p>
        <h2 id="principles-title">Grounded, private, and understandable</h2>
        <div className="principles__grid">
          <article>
            <span aria-hidden="true">01</span>
            <h3>Evidence before answers</h3>
            <p>
              Future lessons will be tied to reviewed or clearly identified
              source material.
            </p>
          </article>
          <article>
            <span aria-hidden="true">02</span>
            <h3>Private by default</h3>
            <p>
              Student-owned records have an explicit ownership and deletion path
              in the schema.
            </p>
          </article>
          <article>
            <span aria-hidden="true">03</span>
            <h3>No ranking</h3>
            <p>
              Progress will describe learning evidence and next actions, never
              compare children.
            </p>
          </article>
        </div>
      </section>
    </main>
  );
}
