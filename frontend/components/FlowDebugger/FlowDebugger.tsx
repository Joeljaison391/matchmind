"use client";
import { useState, useMemo, useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  BackgroundVariant,
  type Node,
  type Edge,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { TraceInfo } from "@/app/types";
import { InputNode, StepNode, EvalNode, OutputNode } from "./flowNodes";
import NodeDetailPanel from "./NodeDetailPanel";

const NODE_TYPES = {
  inputNode: InputNode,
  stepNode: StepNode,
  evalNode: EvalNode,
  outputNode: OutputNode,
};

const CENTER_X = 160;
const Y_GAP = 130;

function buildFlow(trace: TraceInfo, userMessage: string, selectedId: string | null) {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  let y = 0;

  nodes.push({
    id: "input",
    type: "inputNode",
    position: { x: CENTER_X, y },
    data: { message: userMessage },
    draggable: false,
  });
  y += Y_GAP;

  let prevId = "input";

  trace.steps.forEach((step, i) => {
    const id = `step-${i}`;
    nodes.push({
      id,
      type: "stepNode",
      position: { x: CENTER_X, y },
      data: { step, selected: selectedId === id },
      draggable: false,
    });
    edges.push({
      id: `e-${prevId}-${id}`,
      source: prevId,
      target: id,
      animated: true,
      style: { stroke: "#22c55e", strokeWidth: 1.5 },
    });
    prevId = id;
    y += Y_GAP;
  });

  if (trace.eval) {
    nodes.push({
      id: "eval",
      type: "evalNode",
      position: { x: CENTER_X, y },
      data: { eval: trace.eval, marker: trace.retry_marker, selected: selectedId === "eval" },
      draggable: false,
    });
    edges.push({
      id: `e-${prevId}-eval`,
      source: prevId,
      target: "eval",
      animated: true,
      style: { stroke: "#22c55e", strokeWidth: 1.5 },
    });
    prevId = "eval";
    y += Y_GAP;
  }

  nodes.push({
    id: "output",
    type: "outputNode",
    position: { x: CENTER_X, y },
    data: {
      total_ms: trace.total_ms,
      response_type: trace.steps.length > 0 ? trace.steps[trace.steps.length - 1].agent : "response",
    },
    draggable: false,
  });
  edges.push({
    id: `e-${prevId}-output`,
    source: prevId,
    target: "output",
    animated: false,
    style: { stroke: "#4b5563", strokeWidth: 1.5 },
  });

  return { nodes, edges };
}

export default function FlowDebugger({
  trace,
  userMessage,
  responseType,
}: {
  trace: TraceInfo;
  userMessage: string;
  responseType: string;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { nodes, edges } = useMemo(
    () => buildFlow(trace, userMessage, selectedId),
    [trace, userMessage, selectedId]
  );

  const onNodeClick: NodeMouseHandler = useCallback((_evt, node) => {
    setSelectedId((prev) => (prev === node.id ? null : node.id));
  }, []);

  const selectedNode = nodes.find((n) => n.id === selectedId);
  const detailData = selectedNode
    ? selectedNode.id === "input"
      ? { kind: "input" as const, message: userMessage }
      : selectedNode.id === "eval"
      ? { kind: "eval" as const, eval: trace.eval!, marker: trace.retry_marker }
      : selectedNode.id === "output"
      ? { kind: "output" as const, total_ms: trace.total_ms, response_type: responseType }
      : { kind: "step" as const, step: (selectedNode.data as { step: TraceInfo["steps"][0] }).step }
    : null;

  return (
    <div className="relative border border-gray-800 rounded-xl overflow-hidden bg-gray-950" style={{ height: 420 }}>
      <div className="absolute top-2 left-3 z-10 flex items-center gap-2">
        <span className="text-xs text-gray-500 font-medium">Agent Pipeline</span>
        <span className="text-xs text-gray-700">· click any node for details</span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.4}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#1f2937" />
        <Controls
          showInteractive={false}
          className="!bg-gray-900 !border-gray-700 !rounded-lg"
        />
      </ReactFlow>

      {detailData && (
        <NodeDetailPanel data={detailData} onClose={() => setSelectedId(null)} />
      )}
    </div>
  );
}
