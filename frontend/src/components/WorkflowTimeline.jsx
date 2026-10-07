import React from "react";
import "./WorkflowTimeline.css";

const PIPELINE_STAGES = [
  {
    step: "01",
    title: "Data Ingestion",
    description: "Jira REST API, CSV telemetry & execution event streams",
    badge: "Connected",
    icon: "📥",
  },
  {
    step: "02",
    title: "Graph Parsing",
    description: "DAG dependency building & cyclic blocker identification",
    badge: "Indexed",
    icon: "🕸️",
  },
  {
    step: "03",
    title: "Bottleneck Engine",
    description: "SLA risk calculation, cycle detection & idle time scoring",
    badge: "Analyzed",
    icon: "⚡",
  },
  {
    step: "04",
    title: "Hybrid RAG",
    description: "BM25 keyword search + semantic operational synthesis",
    badge: "Active",
    icon: "🧠",
  },
  {
    step: "05",
    title: "Ops Automation",
    description: "Executive dashboards, Slack dispatch & automated remediation",
    badge: "Live",
    icon: "🚀",
  },
];

function WorkflowTimeline() {
  return (
    <div className="pipeline-container">
      <div className="pipeline-header-info">
        <div className="pipeline-pulse-indicator">
          <span className="pulse-dot"></span>
          <span className="pulse-text">End-to-End Autonomous Intelligence Lifecycle</span>
        </div>
        <span className="pipeline-runtime-tag">Pipeline Latency: ~120ms</span>
      </div>

      <div className="pipeline-grid">
        {PIPELINE_STAGES.map((stage, index) => (
          <div key={index} className="pipeline-card">
            <div className="pipeline-card-top">
              <span className="pipeline-step-badge">{stage.step}</span>
              <span className="pipeline-status-badge">{stage.badge}</span>
            </div>
            
            <div className="pipeline-card-body">
              <div className="pipeline-icon">{stage.icon}</div>
              <h3 className="pipeline-title">{stage.title}</h3>
              <p className="pipeline-desc">{stage.description}</p>
            </div>

            {index < PIPELINE_STAGES.length - 1 && (
              <div className="pipeline-connector-arrow">
                <span>→</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default WorkflowTimeline;