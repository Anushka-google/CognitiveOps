import "./MetricCard.css";

function MetricCard({ title, value }) {
  let statusClass = "status-normal";
  let statusBadge = "STABLE";

  const strVal = String(value || "");

  if (title === "Workflow Health") {
    if (strVal.toLowerCase().includes("poor") || strVal.toLowerCase().includes("risk")) {
      statusClass = "status-critical";
      statusBadge = "AT RISK";
    } else {
      statusClass = "status-optimal";
      statusBadge = "OPTIMAL";
    }
  } else if (title === "High Severity" || title === "High Severity Issues") {
    const num = Number(value);
    if (num > 0) {
      statusClass = "status-critical";
      statusBadge = "ESCALATED";
    } else {
      statusClass = "status-optimal";
      statusBadge = "NOMINAL";
    }
  } else if (title === "SLA Risk") {
    if (strVal === "High") {
      statusClass = "status-critical";
      statusBadge = "BREACH RISK";
    } else if (strVal === "Medium") {
      statusClass = "status-warning";
      statusBadge = "ELEVATED";
    } else {
      statusClass = "status-optimal";
      statusBadge = "NORMAL";
    }
  } else if (title === "Poor Executions") {
    const num = Number(value);
    if (num > 0) {
      statusClass = "status-warning";
      statusBadge = "ATTN";
    } else {
      statusClass = "status-optimal";
      statusBadge = "ZERO";
    }
  }

  return (
    <div className={`metric-telemetry-card ${statusClass}`}>
      <div className="metric-telemetry-header">
        <span className="metric-title-text">{title}</span>
        <span className="metric-badge-pill">{statusBadge}</span>
      </div>
      <div className="metric-telemetry-body">
        <span className="metric-number-display">{value}</span>
      </div>
      <div className="metric-telemetry-footer">
        <span className="telemetry-grid-line"></span>
        <span className="telemetry-live-tag">LIVE TELEMETRY</span>
      </div>
    </div>
  );
}

export default MetricCard;
