const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as
  string | undefined;
export const API_BASE_URL = (
  configuredBaseUrl ?? "http://localhost:8000"
).replace(/\/$/, "");

export async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });
  const payload: unknown = await response.json();
  if (!response.ok && response.status !== 503) {
    throw new Error(
      `Backend request failed with status ${String(response.status)}`,
    );
  }
  return payload as T;
}
