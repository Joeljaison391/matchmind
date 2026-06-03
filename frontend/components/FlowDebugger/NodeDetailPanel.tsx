"use client";
import { X } from "lucide-react";
import type { TraceStep } from "@/app/types";

interface DetailData {
  kind: "input" | "step" | "eval" | "output";
  message?: string;
  step?: TraceStep;
  eval?: { relevance: number; completeness: number; accuracy: number; avg: number };
  marker?: string | null;
  total_ms?: number;
  response_type?: string;
}

export default function NodeDetailPanel({
  data,
  onClose,
}: {
  data: DetailData;
  onClose: () => void;
}) {
  return (
    <div className="absolute top-0 right-0 h-full w-72 bg-gray-950 border-l border-gray-800 z-10 overflow-y-auto">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <span className="text-xs font-bold text-gray-300 uppercase tracking-wide">
          {data.kind === "step" ? `${data.step?.agent} · ${data.step?.tool}` : data.kind}
        </span>
        <button onClick={onClose} className="text-gray-600 hover:text-gray-300">
          <X size={14} />
        </button>
      </div>

      <div className="px-4 py-3 space-y-4 text-xs">
        {data.kind === "input" && (
          <div>
            <p className="text-gray-500 uppercase tracking-wide mb-1">Query</p>
            <p className="text-white leading-relaxed">{data.message}</p>
          </div>
        )}

        {data.kind === "step" && data.step && (
          <>
            <Row label="Agent" value={data.step.agent} />
            <Row label="Tool" value={data.step.tool.replace("adk:", "")} />
            <Row label="Latency" value={`${data.step.duration_ms}ms`} />
            {data.step.score != null && (
              <div>
                <p className="text-gray-500 uppercase tracking-wide mb-1">Eval Score</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 rounded-full bg-gray-800">
                    <div
                      className={`h-2 rounded-full ${data.step.score >= 0.75 ? "bg-green-500" : "bg-yellow-500"}`}
                      style={{ width: `${data.step.score * 100}%` }}
                    />
                  </div>
                  <span className="font-mono text-white">{data.step.score.toFixed(3)}</span>
                </div>
              </div>
            )}
            <div>
              <p className="text-gray-500 uppercase tracking-wide mb-1">Input Query</p>
              <p className="text-gray-300 leading-relaxed break-words">{data.step.query}</p>
            </div>
          </>
        )}

        {data.kind === "eval" && data.eval && (
          <>
            <div>
              <p className="text-gray-500 uppercase tracking-wide mb-2">Scores</p>
              {(["relevance", "completeness", "accuracy"] as const).map((dim) => (
                <div key={dim} className="mb-3">
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-400 capitalize">{dim}</span>
                    <span className="font-mono text-white">{data.eval![dim].toFixed(3)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-800">
                    <div
                      className={`h-2 rounded-full transition-all ${data.eval![dim] >= 0.75 ? "bg-green-500" : data.eval![dim] >= 0.5 ? "bg-yellow-500" : "bg-red-500"}`}
                      style={{ width: `${data.eval![dim] * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <Row label="Average" value={data.eval.avg.toFixed(4)} />
            <Row label="Result" value={data.marker ?? "—"} />
            <div className="text-gray-500 mt-2 leading-relaxed">
              Threshold: 0.75 — response {data.marker === "PASS" ? "passed on first attempt" : "triggered a retry with broadened search"}.
            </div>
          </>
        )}

        {data.kind === "output" && (
          <>
            <Row label="Type" value={data.response_type?.replace("_", " ") ?? ""} />
            <Row label="Total latency" value={`${data.total_ms}ms`} />
          </>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-gray-500 uppercase tracking-wide mb-0.5">{label}</p>
      <p className="text-white font-mono">{value}</p>
    </div>
  );
}
