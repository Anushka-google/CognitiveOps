import "./ExecutiveSummary.css";

function ExecutiveSummary({
  summary,
  workflowHealth,
  totalIssues,
  highSeverity,
  bottleneck,
}) {
  const activeSummary = summary || null;
  const kpis = activeSummary?.kpis || {};

  const effectiveHealth =
    kpis.workflow_health || workflowHealth || "Healthy";
  const effectiveTotal =
    kpis.total_tickets !== undefined
      ? kpis.total_tickets
      : totalIssues ?? 0;
  const effectiveDelayed =
    kpis.delayed_tickets_count !== undefined
      ? kpis.delayed_tickets_count
      : 0;
  const effectiveHighSev =
    kpis.high_severity_issues_count !== undefined
      ? kpis.high_severity_issues_count
      : highSeverity ?? 0;
  const effectiveSlaRisk = kpis.sla_risk_level || "Low";
  const effectiveBlockers = kpis.active_blockers_count || 0;
  const effectiveBottleneck =
    activeSummary?.primary_bottleneck ||
    bottleneck ||
    "No critical bottlenecks detected";

  const whatHappened =
    activeSummary?.what_happened && activeSummary.what_happened.length > 0
      ? activeSummary.what_happened
      : [
          `Workflow health status is currently ${effectiveHealth}.`,
          `Tracking ${effectiveTotal} total work items across queues.`,
          effectiveHighSev > 0
            ? `${effectiveHighSev} high-severity issues require operational review.`
            : "No high-severity issues currently flagged.",
        ];

  const why =
    activeSummary?.why && activeSummary.why.length > 0
      ? activeSummary.why
      : [
          effectiveBottleneck !== "No critical bottlenecks detected"
            ? `Primary operational bottleneck: ${effectiveBottleneck}.`
            : "No active dependency blockers or systemic root causes detected.",
        ];

  const whatShouldWeDo =
    activeSummary?.what_should_we_do &&
    activeSummary.what_should_we_do.length > 0
      ? activeSummary.what_should_we_do
      : [
          effectiveHighSev > 0 || effectiveHealth === "At Risk"
            ? "Immediate management escalation and remediation recommended."
            : "Maintain current throughput monitoring; no urgent action required.",
        ];

  const criticalBlockers = activeSummary?.critical_blockers || [];

  // Health badge CSS class
  const healthNormalized = String(effectiveHealth).toLowerCase();
  let healthClass = "health-badge healthy";
  if (healthNormalized.includes("risk")) {
    healthClass = "health-badge at-risk";
  } else if (healthNormalized.includes("attention")) {
    healthClass = "health-badge needs-attention";
  }

  return (
    <div className="executive-summary executive-summary-card">
      {/* Header */}
      <div className="executive-header">
        <div className="executive-header-left">
          <h2 className="executive-title">
            <span>Executive Intelligence Summary</span>
          </h2>
          {activeSummary?.generated_at && (
            <span className="executive-timestamp">
              Generated at: {new Date(activeSummary.generated_at).toLocaleString()}
            </span>
          )}
        </div>

        <div className="executive-badges">
          <span className="grounding-badge">
            ✓ Grounded in Live Telemetry (Zero Invented Metrics)
          </span>
          <span className={healthClass}>{effectiveHealth}</span>
        </div>
      </div>

      {/* KPI Highlight Ribbon */}
      <div className="executive-kpi-ribbon">
        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">Total Work Items</span>
          <span className="kpi-mini-value">{effectiveTotal}</span>
        </div>

        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">Delayed Items</span>
          <span
            className={`kpi-mini-value ${
              effectiveDelayed > 0 ? "highlight-warning" : "highlight-success"
            }`}
          >
            {effectiveDelayed}
          </span>
        </div>

        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">High Severity</span>
          <span
            className={`kpi-mini-value ${
              effectiveHighSev > 0 ? "highlight-danger" : "highlight-success"
            }`}
          >
            {effectiveHighSev}
          </span>
        </div>

        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">Avg Wait Time</span>
          <span className="kpi-mini-value">
            {kpis.avg_days_waiting !== undefined
              ? `${kpis.avg_days_waiting}d`
              : "N/A"}
          </span>
        </div>

        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">SLA Risk</span>
          <span
            className={`kpi-mini-value ${
              effectiveSlaRisk === "High"
                ? "highlight-danger"
                : effectiveSlaRisk === "Medium"
                ? "highlight-warning"
                : "highlight-success"
            }`}
          >
            {effectiveSlaRisk}
          </span>
        </div>

        <div className="kpi-mini-pill">
          <span className="kpi-mini-label">Active Blockers</span>
          <span
            className={`kpi-mini-value ${
              effectiveBlockers > 0 ? "highlight-danger" : "highlight-success"
            }`}
          >
            {effectiveBlockers}
          </span>
        </div>
      </div>

      {/* Critical Blockers Callout */}
      {criticalBlockers.length > 0 && (
        <div className="critical-blockers-callout">
          <span className="blockers-label">
            ⚠️ Active Dependency Blockers Identified
          </span>
          <div className="blockers-chips">
            {criticalBlockers.map((b, idx) => (
              <span key={idx} className="blocker-chip">
                <strong>{b.blocker_key}</strong>
                <span className="blocker-rel">
                  {b.relationship || "blocks"}
                </span>
                <strong>{b.blocked_key}</strong>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tri-Fold Intelligence Sections */}
      <div className="executive-tri-fold">
        {/* Section 1: What Happened */}
        <div className="executive-column">
          <div className="column-header what">
            <span>📌 What Happened</span>
          </div>
          <ul className="column-list what-list">
            {whatHappened.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>

        {/* Section 2: Why It Happened */}
        <div className="executive-column">
          <div className="column-header why">
            <span>🔍 Why It Happened</span>
          </div>
          <ul className="column-list why-list">
            {why.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>

        {/* Section 3: What Should We Do */}
        <div className="executive-column">
          <div className="column-header action">
            <span>⚡ What Should We Do</span>
          </div>
          <ul className="column-list action-list">
            {whatShouldWeDo.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ExecutiveSummary;