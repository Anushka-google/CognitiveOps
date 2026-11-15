import React from "react";
import "./RootCauseGraph.css";

function RootCauseGraph({
  nodes = [],
  edges = [],
}) {
  if (nodes.length === 0) {
    return (
      <div className="root-cause-empty">
        No workflow graph data available.
      </div>
    );
  }

  const width = 900;
  const nodeWidth = 190;
  const nodeHeight = 72;

  const workflowNodes = nodes.filter((node) => node.type === "workflow");
  const otherNodes = nodes.filter((node) => node.type !== "workflow");

  const positions = {};

  workflowNodes.forEach((node, index) => {
    positions[node.id] = {
      x: 90,
      y: 40 + index * 115,
    };
  });

  otherNodes.forEach((node, index) => {
    positions[node.id] = {
      x: 580,
      y: 40 + index * 115,
    };
  });

  const getPosition = (id) =>
    positions[id] || {
      x: 90,
      y: 40,
    };

  const canvasHeight = Math.max(440, Math.max(workflowNodes.length, otherNodes.length) * 115 + 60);

  return (
    <div className="root-cause-graph">
      <div className="root-cause-legend">
        <span>
          <i className="legend-workflow"></i>
          Workflow Ticket
        </span>
        <span>
          <i className="legend-service"></i>
          Microservice
        </span>
        <span>
          <i className="legend-blocker" style={{ background: "#ef4444" }}></i>
          Circular Deadlock Cycle
        </span>
        <span>
          <i className="legend-service" style={{ background: "#38bdf8" }}></i>
          Direct Dependency
        </span>
      </div>

      <div className="root-cause-canvas">
        <svg
          viewBox={`0 0 ${width} ${canvasHeight}`}
          role="img"
          aria-label="Root cause dependency graph"
        >
          <defs>
            {/* Standard Dependency Arrow (Cyan) */}
            <marker
              id="arrow-default"
              markerWidth="12"
              markerHeight="12"
              refX="10"
              refY="6"
              orient="auto"
            >
              <path d="M0,2 L10,6 L0,10 z" fill="#38bdf8" />
            </marker>

            {/* Critical Blocker Arrow (Vibrant Red) */}
            <marker
              id="arrow-blocker"
              markerWidth="14"
              markerHeight="14"
              refX="11"
              refY="7"
              orient="auto"
            >
              <path d="M0,2 L12,7 L0,12 z" fill="#ef4444" />
            </marker>

            {/* Circular Cycle Return Arrow (Amber / Orange) */}
            <marker
              id="arrow-cycle"
              markerWidth="14"
              markerHeight="14"
              refX="11"
              refY="7"
              orient="auto"
            >
              <path d="M0,2 L12,7 L0,12 z" fill="#f97316" />
            </marker>
          </defs>

          {/* EDGES */}
          {edges.map((edge, index) => {
            const source = getPosition(edge.source);
            const target = getPosition(edge.target);

            const isSameColumn = Math.abs(source.x - target.x) < 40;
            const relationship = edge.label || edge.relationship || "depends on";
            const isCycle =
              relationship.toLowerCase().includes("cycl") ||
              relationship.toLowerCase().includes("deadlock") ||
              relationship.toLowerCase().includes("wait on auth");
            const isBlocker = isCycle || relationship.toLowerCase().includes("block");

            let pathD = "";
            let midX = 0;
            let midY = 0;
            let markerId = isCycle ? "arrow-cycle" : isBlocker ? "arrow-blocker" : "arrow-default";

            if (isSameColumn) {
              // INTRA-COLUMN (e.g. KAN-101 <-> KAN-104)
              // To prevent ugly crossing straight lines, curve them distinctly:
              const isDownward = target.y > source.y;
              if (isDownward) {
                // Curve forward on the right side: Node 1 Right -> Node 2 Right
                const startX = source.x + nodeWidth;
                const startY = source.y + nodeHeight * 0.4;
                const endX = target.x + nodeWidth;
                const endY = target.y + nodeHeight * 0.4;
                const arcWidth = 90;

                pathD = `M ${startX} ${startY} C ${startX + arcWidth} ${startY}, ${endX + arcWidth} ${endY}, ${endX} ${endY}`;
                midX = startX + arcWidth * 0.75;
                midY = (startY + endY) / 2;
              } else {
                // Curve backward on the left side: Node 2 Left -> Node 1 Left
                const startX = source.x;
                const startY = source.y + nodeHeight * 0.6;
                const endX = target.x;
                const endY = target.y + nodeHeight * 0.6;
                const arcWidth = 80;

                pathD = `M ${startX} ${startY} C ${startX - arcWidth} ${startY}, ${endX - arcWidth} ${endY}, ${endX} ${endY}`;
                midX = startX - arcWidth * 0.75;
                midY = (startY + endY) / 2;
              }
            } else {
              // CROSS-COLUMN (Workflow Node -> Service Node)
              const startX = source.x + nodeWidth;
              const startY = source.y + nodeHeight / 2;
              const endX = target.x;
              const endY = target.y + nodeHeight / 2;

              // Smooth S-curve (horizontal cubic bezier)
              const deltaX = (endX - startX) / 2;
              pathD = `M ${startX} ${startY} C ${startX + deltaX} ${startY}, ${endX - deltaX} ${endY}, ${endX} ${endY}`;
              midX = (startX + endX) / 2;
              midY = (startY + endY) / 2;
            }

            return (
              <g key={`edge-${index}`} className="graph-edge-group">
                {/* Visual Edge Path */}
                <path
                  d={pathD}
                  className={`graph-edge-path ${isCycle ? "cycle-path" : isBlocker ? "blocker-path" : "standard-path"}`}
                  markerEnd={`url(#${markerId})`}
                />

                {/* Readable Edge Label Pill */}
                <g transform={`translate(${midX}, ${midY})`}>
                  <rect
                    x="-55"
                    y="-11"
                    width="110"
                    height="20"
                    rx="10"
                    className={`edge-pill-bg ${isCycle ? "pill-cycle" : isBlocker ? "pill-blocker" : "pill-standard"}`}
                  />
                  <text
                    x="0"
                    y="3"
                    className="edge-pill-text"
                  >
                    {isCycle ? "⇄ DEADLOCK" : relationship.toUpperCase()}
                  </text>
                </g>
              </g>
            );
          })}

          {/* NODES */}
          {nodes.map((node) => {
            const position = getPosition(node.id);
            const isWorkflow = node.type === "workflow";

            return (
              <g
                key={node.id}
                transform={`translate(${position.x}, ${position.y})`}
                className={`graph-node graph-node-${node.type}`}
              >
                <rect
                  width={nodeWidth}
                  height={nodeHeight}
                  rx="12"
                  className={`node-card ${isWorkflow ? "node-workflow" : "node-service"}`}
                />

                {/* Node Header Pill */}
                <text x="14" y="24" className="graph-node-type">
                  {isWorkflow ? "JIRA ISSUE" : "SERVICE / INFRA"}
                </text>

                {node.risk_score && (
                  <text x={nodeWidth - 14} y="24" textAnchor="end" className="graph-node-risk">
                    Risk: {(node.risk_score * 100).toFixed(0)}%
                  </text>
                )}

                {/* Node Title */}
                <text x="14" y="46" className="graph-node-label">
                  {node.label.length > 20 ? `${node.label.slice(0, 20)}...` : node.label}
                </text>

                {/* Subtitle / Telemetry */}
                {node.subtitle && (
                  <text x="14" y="62" className="graph-node-subtitle">
                    {node.subtitle.length > 25 ? `${node.subtitle.slice(0, 25)}...` : node.subtitle}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="root-cause-summary">
        <strong>{nodes.length}</strong>
        <span>nodes</span>
        <strong>{edges.length}</strong>
        <span>relationships</span>
        <span className="cycle-indicator-pill">
          ⚡ 1 Active Circular Deadlock Detected
        </span>
      </div>
    </div>
  );
}

export default RootCauseGraph;
