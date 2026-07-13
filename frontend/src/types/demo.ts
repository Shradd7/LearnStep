export interface DemoProfile {
  class_level: number;
  subject: "mathematics" | "science";
}

export interface DemoLoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in_seconds: number;
  account_label: string;
  profile: DemoProfile;
  notice_version: string;
  limitations: string[];
}

export interface DemoSource {
  source_id: string;
  label: string;
  page: number;
}

export interface DemoChapter {
  package_key: string;
  title: string;
  class_level: number;
  subject: string;
  concept_key: string;
  review_status: string;
  source: DemoSource;
  confidence: string;
}

export interface DemoDocument {
  id: string;
  display_name: string;
  class_level: number;
  subject: string;
  status: string;
  expires_at: string;
  detected_concepts: string[];
  chunk_count: number;
  extraction_pipeline_version: string;
}

export interface DemoSession {
  session_id: string;
  package_key: string;
  title: string;
  review_status: string;
  confidence: string;
  lesson: {
    goal: string;
    prerequisites: string;
    explanation: string;
    example: string;
    recap: string;
  };
  question: {
    question_key: string;
    text: string;
    answer_type: string;
    options: string[];
    cognitive_level: string;
    difficulty: string;
  };
  source: DemoSource;
  evidence_chunk_ids: string[];
  known_limitations: string[];
}

export interface DemoHint {
  session_id: string;
  level: number;
  hint: string;
  answer_revealed: false;
}

export interface DemoAttempt {
  attempt_id: string;
  outcome: "correct" | "incorrect" | "needs_review";
  confidence: string;
  feedback: string;
  explanation: string;
  accepted_answer: string;
  features: Record<string, unknown>;
  hint_count: number;
}

export interface DemoProgress {
  policy_version: string;
  observations: Array<{
    concept_key: string;
    attempts_observed: number;
    correct_observations: number;
    supported_observations: number;
    next_action: string;
  }>;
  limitation: string;
}
