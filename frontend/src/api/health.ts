import { requestJson } from "./client";
import type { ReadyHealth } from "../types/health";

export function getBackendReadiness(
  signal?: AbortSignal,
): Promise<ReadyHealth> {
  return requestJson<ReadyHealth>("/health/ready", { signal });
}
