"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";
import type { Message } from "./types";
import MessageBubble from "@/components/Chat/MessageBubble";
import { sendMessage } from "@/lib/api";

const CHIPS = [
  { label: "When does Brazil play?",              icon: "🇧🇷" },
  { label: "Find halal food near MetLife Stadium", icon: "🍽" },
  { label: "Plan my day from downtown Dallas",     icon: "🗺" },
  { label: "How many teams in the World Cup?",     icon: "❓" },
  { label: "¿Cuándo juega Argentina?",             icon: "🇦🇷" },
];

const FEATURES = [
  { icon: "🏟", title: "Match Schedule", desc: "Every fixture, kickoff time, group, and broadcaster — in any language." },
  { icon: "🍽", title: "Food & Drink",   desc: "Halal, vegan, and local spots near every stadium, ranked by distance." },
  { icon: "🗺", title: "Your Journey",   desc: "Step-by-step match day plans with transport from your hotel." },
];

function randomId() {
  return Math.random().toString(36).slice(2, 10);
}

function getOrCreateSession() {
  if (typeof window === "undefined") return randomId();
  const key = "matchmind_session";
  let id = sessionStorage.getItem(key);
  if (!id) { id = randomId(); sessionStorage.setItem(key, id); }
  return id;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(getOrCreateSession);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const submit = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { id: randomId(), role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendMessage(trimmed, sessionId);
      setMessages((prev) => [
        ...prev,
        {
          id: randomId(),
          role: "assistant",
          text: data.response.text,
          payload: data.response,
          trace: data.trace,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: randomId(), role: "assistant", text: "Couldn't reach the backend — is it running?" },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [loading, sessionId]);

  return (
    <div className="flex flex-col h-screen" style={{ background: "#08090e" }}>
      {/* ── header ── */}
      <header className="shrink-0 border-b border-gray-800/60 px-5 py-3 flex items-center justify-between"
        style={{ background: "linear-gradient(90deg, #0b1a0f 0%, #08090e 60%)" }}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center text-base shadow-lg shadow-green-900/50">
            ⚽
          </div>
          <div>
            <div className="font-bold text-white text-base leading-none">MatchMind</div>
            <div className="text-[10px] text-green-600 font-semibold tracking-widest uppercase mt-0.5">
              FIFA World Cup 2026™
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs text-gray-600 font-mono hidden sm:block">{sessionId}</span>
        </div>
      </header>

      {/* ── message thread ── */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-5">

        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center min-h-full gap-8 py-8">

            {/* hero */}
            <div className="text-center space-y-3 max-w-md">
              <div className="text-5xl mb-2">🏆</div>
              <h1 className="text-3xl font-bold text-white leading-tight">
                Your World Cup<br />
                <span className="text-green-500">AI Concierge</span>
              </h1>
              <p className="text-gray-500 text-sm leading-relaxed">
                Matches, food, transport, and local secrets — across 16 cities,
                32 teams, and 12+ languages.
              </p>
            </div>

            {/* feature pillars */}
            <div className="grid grid-cols-3 gap-3 w-full max-w-lg">
              {FEATURES.map((f) => (
                <div key={f.title}
                  className="bg-[#0f1015] border border-gray-800 rounded-2xl p-3 text-center space-y-1.5 hover:border-green-900 transition-colors">
                  <span className="text-2xl">{f.icon}</span>
                  <p className="text-xs font-semibold text-white">{f.title}</p>
                  <p className="text-[11px] text-gray-600 leading-relaxed hidden sm:block">{f.desc}</p>
                </div>
              ))}
            </div>

            {/* chips */}
            <div className="w-full max-w-lg">
              <p className="text-xs text-gray-600 text-center mb-3 uppercase tracking-widest">Try asking</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {CHIPS.map((c) => (
                  <button key={c.label} onClick={() => submit(c.label)}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border border-gray-800 text-gray-400 bg-[#0f1015] hover:border-green-700 hover:text-green-400 hover:bg-green-950/20 transition-all">
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-600 text-sm">
            <Loader2 size={14} className="animate-spin text-green-600" />
            <span>Thinking…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* ── chips strip ── */}
      {messages.length > 0 && (
        <div className="shrink-0 px-4 py-2 border-t border-gray-800/60 flex gap-2 overflow-x-auto"
          style={{ background: "#08090e" }}>
          {CHIPS.map((c) => (
            <button key={c.label} onClick={() => submit(c.label)}
              className="flex items-center gap-1 text-xs px-3 py-1 rounded-full border border-gray-800 text-gray-500 whitespace-nowrap hover:border-green-800 hover:text-green-400 transition-all shrink-0">
              <span>{c.icon}</span>
              <span>{c.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* ── input bar ── */}
      <div className="shrink-0 px-4 pb-4 pt-2" style={{ background: "#08090e" }}>
        <form onSubmit={(e) => { e.preventDefault(); submit(input); }}
          className="flex items-center gap-3 rounded-2xl px-4 py-3 border border-gray-800 focus-within:border-green-700 transition-colors"
          style={{ background: "#0f1015" }}>
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about the World Cup…"
            className="flex-1 bg-transparent text-sm text-white placeholder-gray-700 outline-none"
            disabled={loading}
          />
          <button type="submit" disabled={!input.trim() || loading}
            className="w-8 h-8 rounded-full bg-green-600 disabled:bg-gray-800 flex items-center justify-center transition-colors hover:bg-green-500 shrink-0">
            {loading
              ? <Loader2 size={14} className="animate-spin text-white" />
              : <Send size={14} className="text-white" />}
          </button>
        </form>
      </div>
    </div>
  );
}
