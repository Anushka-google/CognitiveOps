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
  const nodeWidth = 180;
  const nodeHeight = 70;

  const workflowNodes =
    nodes.filter(
      (node) =>
        node.type === "workflow"
    );

  const otherNodes =
    nodes.filter(
      (node) =>
        node.type !== "workflow"
    );

  const positions = {};

  workflowNodes.forEach(
    (node, index) => {

      positions[node.id] = {
        x: 80,
        y: 40 + index * 105,
      };

    }
  );

  otherNodes.forEach(
    (node, index) => {

      positions[node.id] = {
        x: 560,
        y: 40 + index * 105,
      };

    }
  );

  const getPosition = (id) =>
    positions[id] || {
      x: 80,
      y: 40,
    };

  return (
    <div className="root-cause-graph">

      <div className="root-cause-legend">

        <span>
          <i className="legend-workflow"></i>
          Workflow
        </span>

        <span>
          <i className="legend-owner"></i>
          Owner
        </span>

        <span>
          <i className="legend-service"></i>
          Service
        </span>

        <span>
          <i className="legend-blocker"></i>
          Dependency
        </span>

      </div>

      <div className="root-cause-canvas">

        <svg
          viewBox={`0 0 ${width} ${Math.max(
            420,
            nodes.length * 105
          )}`}
          role="img"
          aria-label="Root cause dependency graph"
        >

          <defs>

            <marker
              id="root-cause-arrow"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >

              <path
                d="M0,0 L0,6 L9,3 z"
                className="graph-arrow"
              />

            </marker>

          </defs>

          {/* EDGES */}

          {edges.map(
            (
              edge,
              index
            ) => {

              const source =
                getPosition(
                  edge.source
                );

              const target =
                getPosition(
                  edge.target
                );

              const x1 =
                source.x + nodeWidth;

              const y1 =
                source.y + nodeHeight / 2;

              const x2 =
                target.x;

              const y2 =
                target.y + nodeHeight / 2;

              return (
                <g key={index}>

                  <line
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    className={
                      edge.relationship === "blocks"
                        ? "graph-edge blocker-edge"
                        : "graph-edge"
                    }
                    markerEnd="url(#root-cause-arrow)"
                  />

                  <text
                    x={(x1 + x2) / 2}
                    y={(y1 + y2) / 2 - 8}
                    className="graph-edge-label"
                  >
                    {edge.relationship}
                  </text>

                </g>
              );
            }
          )}

          {/* NODES */}

          {nodes.map(
            (
              node
            ) => {

              const position =
                getPosition(
                  node.id
                );

              return (
                <g
                  key={node.id}
                  transform={
                    `translate(${position.x}, ${position.y})`
                  }
                  className={
                    `graph-node graph-node-${node.type}`
                  }
                >

                  <rect
                    width={nodeWidth}
                    height={nodeHeight}
                    rx="12"
                  />

                  <text
                    x="14"
                    y="27"
                    className="graph-node-type"
                  >
                    {node.type.toUpperCase()}
                  </text>

                  <text
                    x="14"
                    y="49"
                    className="graph-node-label"
                  >
                    {
                      node.label.length > 22
                        ? `${node.label.slice(0, 22)}...`
                        : node.label
                    }
                  </text>

                </g>
              );
            }
          )}

        </svg>

      </div>

      <div className="root-cause-summary">

        <strong>
          {nodes.length}
        </strong>

        <span>
          nodes
        </span>

        <strong>
          {edges.length}
        </strong>

        <span>
          relationships
        </span>

      </div>

      {
        edges.length === 0 && (
          <div className="root-cause-no-links">
            No explicit Jira issue dependencies
            were found in the current project.
          </div>
        )
      }

    </div>
  );
}

export default RootCauseGraph;