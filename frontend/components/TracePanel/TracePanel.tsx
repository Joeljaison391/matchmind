"use client";
import { useState } from "react";
import type { TraceInfo } from "@/app/types";
import { ChevronDown, ChevronUp } from "lucide-react";

const AGENT_COLOR: Record<string, string> = {
  router: "text-blue-400",
  match_agent: "text-purple-400",
  discovery_agent: "text-yellow-400",
  logistics_agent: "text-orange-400",
  memory_agent: "text-pink-400",
};

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 0.75 ? "text-green-400" : score >= 0.5 ? "text-yellow-400" : "text-red-400";
  return <span className={`font-mono text-xs ${color}`}>{score.toFixed(2)}</span>;
}

export default function TracePanel({ trace, embedded = false }: { trace: TraceInfo; embedded?: boolean }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={embedded ? "bg-gray-950" : "border-t border-gray-800 bg-gray-950"}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-gray-600">{trace.agents_fired.join(" → ")}</span>
          {trace.eval && (
            <span className="flex items-center gap-1">
              <span
                className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                  trace.retry_marker === "PASS"
                    ? "bg-green-900/40 text-green-400"
                    : "bg-yellow-900/40 text-yellow-400"
                }`}
              >
                {trace.retry_marker}
              </span>
              <ScoreBadge score={trace.eval.avg} />
            </span>
          )}
        </div>
        {open ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3">
          {trace.steps.map((step, i) => (
            <div key={i} className="flex items-start gap-3 text-xs">
              <span className={`font-medium w-28 shrink-0 ${AGENT_COLOR[step.agent] ?? "text-gray-400"}`}>
                {step.agent}
              </span>
              <span className="text-gray-500 w-36 shrink-0">{step.tool}</span>
              <span className="text-gray-600 flex-1 truncate">{step.query}</span>
              <span className="text-gray-600 w-12 text-right">{step.duration_ms}ms</span>
              <span className="w-10 text-right">
                {step.score != null ? <ScoreBadge score={step.score} /> : <span className="text-gray-700">—</span>}
              </span>
            </div>
          ))}

          {trace.eval && (
            <div className="pt-2 border-t border-gray-800 flex items-center gap-4 text-xs text-gray-500">
              <span>Eval</span>
              <span>relevance <ScoreBadge score={trace.eval.relevance} /></span>
              <span>completeness <ScoreBadge score={trace.eval.completeness} /></span>
              <span>accuracy <ScoreBadge score={trace.eval.accuracy} /></span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
