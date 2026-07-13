export function AboutPage() {
  return (
    <main id="main-content" className="text-page">
      <p className="eyebrow">About LearnStep</p>
      <h1>Upload. Learn. Ace it.</h1>
      <p>
        Students often struggle not because they cannot learn, but because the
        explanation is too advanced, too generic, or disconnected from their own
        chapter. We wanted to create a study buddy that adapts to a
        student&apos;s class, subject, and uploaded material—without making
        learning feel like another boring worksheet.
      </p>
      <p>
        LearnStep is an NLP-first learning companion for Classes 5–8 Mathematics
        and Science.
      </p>
      <p>
        Students upload a chapter PDF, notes, or worksheet. LearnStep extracts
        concepts, definitions, formulas, examples, and exercises; turns them
        into short lessons; asks class-appropriate questions; gives hints before
        solutions; and recommends what to revise next.
      </p>
      <p>
        Instead of calling students “weak” or “smart,” it tracks learning
        evidence such as:
      </p>
      <ul>
        <li>Introduced</li>
        <li>Developing with support</li>
        <li>Demonstrated independently</li>
        <li>Ready for revision</li>
      </ul>
      <div className="notice" role="note">
        This portfolio demo uses synthetic sample accounts and original
        synthetic content. It is not an official curriculum product. A real
        child-facing release still requires qualified privacy and educational
        review.
      </div>
    </main>
  );
}
