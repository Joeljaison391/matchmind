"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";
import type { Message } from "./types";
import MessageBubble from "@/components/Chat/MessageBubble";
import { sendMessage } from "@/lib/api";

const CHIPS = [
  "When does Brazil play?",
  "Find halal food near MetLife Stadium",
  "Plan my day from downtown Dallas",
  "How many teams are in the World Cup?",
  "¿Cuándo juega Argentina?",
];

function randomId() {
  return Math.random().toString(36).slice(2, 10);
}

function getOrCreateSession() {
  if (typeof window === "undefined") return randomId();
  const key = "matchmind_session";
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = randomId();
    sessionStorage.setItem(key, id);
  }
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

  const submit = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      const userMsg: Message = { id: randomId(), role: "user", text: trimmed };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setLoading(true);

      try {
        const data = await sendMessage(trimmed, sessionId);
        const botMsg: Message = {
          id: randomId(),
          role: "assistant",
          text: data.response.text,
          payload: data.response,
          trace: data.trace,
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            id: randomId(),
            role: "assistant",
            text: "Something went wrong — check the backend is running.",
          },
        ]);
      } finally {
        setLoading(false);
        inputRef.current?.focus();
      }
    },
    [loading, sessionId]
  );

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* header */}
      <header className="flex items-center justify-between px-5 py-3 border-b border-gray-800 shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-xl">⚽</span>
          <span className="font-bold text-white text-lg">MatchMind</span>
          <span className="text-xs text-gray-500 ml-1">FIFA World Cup 2026</span>
        </div>
        <span className="text-xs text-gray-600 font-mono">{sessionId}</span>
      </header>

      {/* message thread */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 text-center">
            <div>
              <p className="text-3xl font-bold text-white">Your World Cup AI</p>
              <p className="text-gray-500 mt-2 text-sm max-w-sm">
                Ask about matches, food, transport, or plans — in any language.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
              {CHIPS.map((chip) => (
                <button
                  key={chip}
                  onClick={() => submit(chip)}
                  className="text-xs px-3 py-1.5 rounded-full border border-gray-700 text-gray-400 hover:border-green-500 hover:text-green-400 transition-colors"
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Loader2 size={14} className="animate-spin" />
            <span>Thinking…</span>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* chips strip — shown after first message */}
      {messages.length > 0 && (
        <div className="px-4 py-2 flex gap-2 overflow-x-auto shrink-0 border-t border-gray-800">
          {CHIPS.map((chip) => (
            <button
              key={chip}
              onClick={() => submit(chip)}
              className="text-xs px-3 py-1 rounded-full border border-gray-800 text-gray-500 hover:border-green-600 hover:text-green-400 whitespace-nowrap transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* input bar */}
      <div className="px-4 pb-4 shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit(input);
          }}
          className="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-2xl px-4 py-3 focus-within:border-green-600 transition-colors"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about the World Cup…"
            className="flex-1 bg-transparent text-sm text-white placeholder-gray-600 outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="text-green-500 disabled:text-gray-700 hover:text-green-400 transition-colors"
          >
            {loading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
