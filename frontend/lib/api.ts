import type { ChatApiResponse } from "@/app/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function sendMessage(
  message: string,
  sessionId: string,
  languageHint?: string
): Promise<ChatApiResponse> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, language_hint: languageHint }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function getMemory(sessionId: string) {
  const res = await fetch(`${BASE}/api/memory/${sessionId}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
