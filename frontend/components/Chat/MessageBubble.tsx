"use client";
import { useState } from "react";
import { GitBranch, List } from "lucide-react";
import type { Message } from "@/app/types";
import ResponseRenderer from "./ResponseRenderer";
import TracePanel from "@/components/TracePanel/TracePanel";
import dynamic from "next/dynamic";

// lazy-load React Flow so it doesn't block initial page render
const FlowDebugger = dynamic(
  () => import("@/components/FlowDebugger/FlowDebugger"),
  { ssr: false, loading: () => <div className="h-24 flex items-center justify-center text-xs text-gray-600">Loading debugger…</div> }
);

type TraceView = "trace" | "flow";

export default function MessageBubble({ message }: { message: Message }) {
  const [traceView, setTraceView] = useState<TraceView>("trace");
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-green-600 text-white rounded-2xl rounded-br-sm px-4 py-2 text-sm">
          {message.text}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <div className="max-w-[90%]">
        {message.payload ? (
          <ResponseRenderer payload={message.payload} />
        ) : (
          <p className="text-sm text-gray-300">{message.text}</p>
        )}
      </div>

      {message.trace && (
        <div className="border border-gray-800 rounded-xl overflow-hidden bg-gray-950">
          {/* tab bar */}
          <div className="flex items-center border-b border-gray-800">
            <button
              onClick={() => setTraceView("trace")}
              className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors ${
                traceView === "trace"
                  ? "text-white border-b-2 border-green-500"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              <List size={12} />
              Trace
            </button>
            <button
              onClick={() => setTraceView("flow")}
              className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors ${
                traceView === "flow"
                  ? "text-white border-b-2 border-green-500"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              <GitBranch size={12} />
              Flow
            </button>
            <span className="ml-auto pr-3 text-xs text-gray-600 font-mono">
              {message.trace.total_ms}ms
            </span>
          </div>

          {/* content */}
          {traceView === "trace" ? (
            <TracePanel trace={message.trace} embedded />
          ) : (
            <div className="p-2">
              <FlowDebugger
                trace={message.trace}
                userMessage={message.text}
                responseType={message.payload?.type ?? "response"}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
