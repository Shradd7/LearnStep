# Child safety and privacy boundary

LearnStep is currently a controlled portfolio demonstration, not a child-facing release.

## Data minimization

- Only synthetic `.invalid` accounts are available; there is no registration form.
- The demo does not request name, school, date of birth, address, phone, photograph, or parent/teacher details.
- The UI warns users not to upload real student work or enter real child information.
- Tokens live in browser memory, not persistent web storage.
- Uploaded bytes live in private storage under generated keys, never relational rows or public paths.
- Raw PDF text, answers, tokens, filenames, and embeddings are not intentionally logged.

## Retention and deletion

Uploads expire after 60 minutes by default. The API periodically removes expired files and database rows, and owner-authorized explicit deletion removes the private file and cascades chunks. The integration test verifies physical fixture-file deletion and derived-row deletion. Production storage must add a provider lifecycle rule as an independent backstop.

## Learning evidence

Progress keeps curriculum coverage, observed evidence, and next action conceptually separate. Current output uses observation counts and support use. It does not rank students, compare users, infer intelligence/personality/attention/disability/emotion, or claim mastery from one answer.

## Unresolved review

A real release requires qualified privacy/legal review, educational-content review, age-appropriate terms and consent decisions, deployment-specific retention approval, incident handling, and operational monitoring. These technical controls are not a legal-compliance claim.
