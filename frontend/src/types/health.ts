export interface LiveHealth {
  status: "alive";
  service: string;
  environment: string;
}

export interface ReadyHealth {
  status: "ready" | "not_ready";
  checks: Record<string, boolean>;
  embedding_model: string;
  embedding_dimension: number;
}

export type HealthViewState =
  | { phase: "loading" }
  | { phase: "ready"; health: ReadyHealth }
  | { phase: "unavailable"; health: ReadyHealth }
  | { phase: "error"; message: string };
