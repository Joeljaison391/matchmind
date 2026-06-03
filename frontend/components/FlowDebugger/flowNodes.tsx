"use client";
import { Handle, Position } from "@xyflow/react";
import type { TraceStep } from "@/app/types";

const AGENT_COLORS: Record<string, { border: string; badge: string; dot: string }> = {
  memory_agent:    { border: "border-pink-500",   badge: "bg-pink-900/60 text-pink-300",   dot: "bg-pink-500" },
  router:          { border: "border-blue-500",   badge: "bg-blue-900/60 text-blue-300",   dot: "bg-blue-500" },
  match_agent:     { border: "border-purple-500", badge: "bg-purple-900/60 text-purple-300", dot: "bg-purple-500" },
  discovery_agent: { border: "border-yellow-500", badge: "bg-yellow-900/60 text-yellow-400", dot: "bg-yellow-500" },
  logistics_agent: { border: "border-orange-500", badge: "bg-orange-900/60 text-orange-300", dot: "bg-orange-500" },
};

function agentStyle(name: string) {
  return AGENT_COLORS[name] ?? { border: "border-gray-500", badge: "bg-gray-800 text-gray-300", dot: "bg-gray-500" };
}

// ── Input node ─────────────────────────────────────────────────────────────

export function InputNode({ data }: { data: { message: string } }) {
  return (
    <div className="bg-gray-900 border-2 border-green-500 rounded-2xl px-4 py-3 w-64 shadow-lg shadow-green-500/10">
      <div className="flex items-center gap-2 mb-1">
        <span className="w-2 h-2 rounded-full bg-green-500" />
        <span className="text-xs font-bold text-green-400 uppercase tracking-wide">User Query</span>
      </div>
      <p className="text-sm text-white truncate">{data.message}</p>
      <Handle type="source" position={Position.Bottom} className="!bg-green-500 !w-2 !h-2" />
    </div>
  );
}

// ── Step node (agent + tool call) ──────────────────────────────────────────

export function StepNode({ data }: { data: { step: TraceStep; selected: boolean } }) {
  const { step } = data;
  const s = agentStyle(step.agent);
  const toolName = step.tool.replace("adk:", "");

  return (
    <div
      className={`bg-gray-900 border-2 ${s.border} rounded-xl px-4 py-3 w-64 shadow-lg cursor-pointer transition-all ${
        data.selected ? "ring-2 ring-white/30" : "hover:brightness-110"
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-600 !w-2 !h-2" />

      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${s.badge}`}>
          {step.agent.replace("_", " ")}
        </span>
        <span className="text-xs text-gray-500 font-mono">{step.duration_ms}ms</span>
      </div>

      <div className="flex items-center gap-1.5">
        <span className="text-gray-500 text-xs">⚙</span>
        <span className="text-sm text-white font-medium truncate">{toolName}</span>
      </div>

      {step.score != null && (
        <div className="mt-2 flex items-center gap-2">
          <div className="flex-1 h-1 rounded-full bg-gray-800">
            <div
              className={`h-1 rounded-full ${step.score >= 0.75 ? "bg-green-500" : step.score >= 0.5 ? "bg-yellow-500" : "bg-red-500"}`}
              style={{ width: `${step.score * 100}%` }}
            />
          </div>
          <span className={`text-xs font-mono ${step.score >= 0.75 ? "text-green-400" : "text-yellow-400"}`}>
            {step.score.toFixed(2)}
          </span>
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-gray-600 !w-2 !h-2" />
    </div>
  );
}

// ── Eval node ─────────────────────────────────────────────────────────────

export function EvalNode({
  data,
}: {
  data: {
    eval: { relevance: number; completeness: number; accuracy: number; avg: number };
    marker: string | null;
  };
}) {
  const pass = data.marker === "PASS";
  return (
    <div
      className={`bg-gray-900 border-2 ${pass ? "border-green-500" : "border-yellow-500"} rounded-xl px-4 py-3 w-64 shadow-lg cursor-pointer`}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-600 !w-2 !h-2" />

      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">Evaluator</span>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            pass ? "bg-green-900/60 text-green-400" : "bg-yellow-900/60 text-yellow-400"
          }`}
        >
          {data.marker ?? "—"}
        </span>
      </div>

      {(["relevance", "completeness", "accuracy"] as const).map((dim) => (
        <div key={dim} className="flex items-center gap-2 mb-1">
          <span className="text-xs text-gray-500 w-24 capitalize">{dim}</span>
          <div className="flex-1 h-1.5 rounded-full bg-gray-800">
            <div
              className={`h-1.5 rounded-full ${data.eval[dim] >= 0.75 ? "bg-green-500" : "bg-yellow-500"}`}
              style={{ width: `${data.eval[dim] * 100}%` }}
            />
          </div>
          <span className="text-xs font-mono text-gray-400 w-8">{data.eval[dim].toFixed(2)}</span>
        </div>
      ))}

      <div className={`mt-2 text-center text-sm font-bold ${pass ? "text-green-400" : "text-yellow-400"}`}>
        avg {data.eval.avg.toFixed(3)}
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-gray-600 !w-2 !h-2" />
    </div>
  );
}

// ── Output node ────────────────────────────────────────────────────────────

export function OutputNode({ data }: { data: { total_ms: number; response_type: string } }) {
  return (
    <div className="bg-gray-900 border-2 border-gray-600 rounded-2xl px-4 py-3 w-64 shadow-lg">
      <Handle type="target" position={Position.Top} className="!bg-gray-600 !w-2 !h-2" />
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-gray-400" />
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">Response</span>
        <span className="ml-auto text-xs text-gray-500 font-mono">{data.total_ms}ms total</span>
      </div>
      <p className="text-sm text-gray-300 mt-1 capitalize">{data.response_type.replace("_", " ")}</p>
    </div>
  );
}
