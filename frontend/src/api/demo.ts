import { requestJson } from "./client";
import type {
  DemoAttempt,
  DemoChapter,
  DemoDocument,
  DemoHint,
  DemoLoginResponse,
  DemoProgress,
  DemoSession,
} from "../types/demo";

function authorized(token: string, init?: RequestInit): RequestInit {
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return { ...init, headers };
}

export function loginDemo(
  email: string,
  password: string,
): Promise<DemoLoginResponse> {
  return requestJson<DemoLoginResponse>("/api/v1/demo/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function getDemoChapters(token: string): Promise<DemoChapter[]> {
  return requestJson<DemoChapter[]>("/api/v1/demo/chapters", authorized(token));
}

export function uploadDemoDocument(
  token: string,
  file: File,
  classLevel: number,
  subject: string,
): Promise<DemoDocument> {
  const body = new FormData();
  body.set("file", file);
  body.set("class_level", String(classLevel));
  body.set("subject", subject);
  return requestJson<DemoDocument>(
    "/api/v1/documents",
    authorized(token, { method: "POST", body }),
  );
}

export function startDemoSession(
  token: string,
  packageKey: string,
  documentId?: string,
): Promise<DemoSession> {
  return requestJson<DemoSession>(
    "/api/v1/demo/sessions",
    authorized(token, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        package_key: packageKey,
        document_id: documentId ?? null,
      }),
    }),
  );
}

export function revealDemoHint(
  token: string,
  sessionId: string,
  level: number,
): Promise<DemoHint> {
  return requestJson<DemoHint>(
    `/api/v1/demo/sessions/${sessionId}/hints/${String(level)}`,
    authorized(token, { method: "POST" }),
  );
}

export function submitDemoAttempt(
  token: string,
  sessionId: string,
  response: string,
): Promise<DemoAttempt> {
  return requestJson<DemoAttempt>(
    `/api/v1/demo/sessions/${sessionId}/attempts`,
    authorized(token, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ response }),
    }),
  );
}

export function getDemoProgress(token: string): Promise<DemoProgress> {
  return requestJson<DemoProgress>("/api/v1/demo/progress", authorized(token));
}
