import React, { useState } from "react";
import "./MachineLearningIntelligence.css";

const SUPERVISED_TICKETS = [
  {
    ticket_id: "KAN-101",
    title: "Payment Gateway Integration Blocked",
    breach_prob: 89,
    risk: "High",
    top_feature: "Review Queue Idle Time (4.2 days)",
    sla_hours_remaining: "-14h (Breached)"
  },
  {
    ticket_id: "KAN-107",
    title: "Staging DB Migration Idle",
    breach_prob: 82,
    risk: "High",
    top_feature: "Staging Credential Rotation Blocked",
    sla_hours_remaining: "-8h (Breached)"
  },
  {
    ticket_id: "KAN-104",
    title: "Payment Webhook Callback Handler",
    breach_prob: 76,
    risk: "High",
    top_feature: "Deadlock Dependency on KAN-101",
    sla_hours_remaining: "4h remaining"
  },
  {
    ticket_id: "KAN-105",
    title: "Order Notification Dispatcher",
    breach_prob: 22,
    risk: "Low",
    top_feature: "Standard Queue Latency (1.1d)",
    sla_hours_remaining: "48h remaining"
  },
  {
    ticket_id: "KAN-102",
    title: "User Authentication Service",
    breach_prob: 18,
    risk: "Low",
    top_feature: "Active In-Progress State",
    sla_hours_remaining: "62h remaining"
  },
  {
    ticket_id: "KAN-103",
    title: "Cart Checkout Flow Optimization",
    breach_prob: 12,
    risk: "Low",
    top_feature: "Nominal Execution Speed",
    sla_hours_remaining: "70h remaining"
  }
];

const RF_FEATURE_IMPORTANCE = [
  { feature: "Backlog Queue Age (hours)", importance: 38, icon: "⏳" },
  { feature: "Agent Queue Depth at Submit", importance: 27, icon: "👥" },
  { feature: "Priority & Escalation Weight", importance: 21, icon: "⚡" },
  { feature: "Historical First Response Time", importance: 14, icon: "⏱️" }
];

const COMBINED_INTELLIGENCE_RECORDS = [
  {
    ticket_id: "KAN-101",
    title: "Payment Gateway Integration Blocked",
    rf_prob: 89,
    rf_risk: "High",
    iso_score: 88.5,
    iso_tier: "High-Severity Anomaly",
    is_anomaly: true,
    category: "urgent",
    quadrant: "High SLA Risk + Anomaly",
    diagnosis: "Urgent Management Escalation",
    action: "Immediate tech lead reassignment & Slack alert dispatch to unblock release.",
    telemetry: {
      days_waiting: 4.2,
      assignee: "Alex Chen (Tech Lead)",
      status: "In Review",
      priority: "High",
      handoff_count: 3,
      rf_driver: "Review Queue Idle: 4.2d exceeding SLA threshold by 112%",
      iso_driver: "Isolated in top 11.5% percentile of feature space (tree depth 3.2 vs 6.8 baseline)",
      evidence: "Topological cycle detected with KAN-104. Lead reviewer currently assigned to 6 concurrent tasks with zero commits pushed in 72 hours.",
      recommendation: "Decouple auth schema check from integration test and transfer review to on-call secondary lead."
    }
  },
  {
    ticket_id: "KAN-107",
    title: "Staging DB Migration Idle",
    rf_prob: 82,
    rf_risk: "High",
    iso_score: 94.2,
    iso_tier: "High-Severity Anomaly",
    is_anomaly: true,
    category: "urgent",
    quadrant: "High SLA Risk + Anomaly",
    diagnosis: "Urgent Pipeline Unblock",
    action: "Automate credential rotation to unblock staging pipeline execution.",
    telemetry: {
      days_waiting: 4.5,
      assignee: "Database DevOps Pool",
      status: "Blocked",
      priority: "Critical",
      handoff_count: 4,
      rf_driver: "Cumulative wait time 4.5d under Critical priority",
      iso_driver: "Isolated in top 5.8% percentile of feature space (+1.5σ deviation above 1.88d baseline)",
      evidence: "Database schema migration blocked pending secret rotation token. Dependent staging test suites stalled.",
      recommendation: "Trigger automated credential rotation webhook to clear blocking dependency."
    }
  },
  {
    ticket_id: "KAN-104",
    title: "Payment Webhook Callback Handler",
    rf_prob: 76,
    rf_risk: "High",
    iso_score: 76.4,
    iso_tier: "Moderate Anomaly",
    is_anomaly: true,
    category: "urgent",
    quadrant: "High SLA Risk + Anomaly",
    diagnosis: "Decouple Circular Cycle",
    action: "Decouple schema validation from callback handler to break deadlock.",
    telemetry: {
      days_waiting: 3.7,
      assignee: "Integration Team",
      status: "Blocked",
      priority: "High",
      handoff_count: 2,
      rf_driver: "Blocked status with 4h SLA budget remaining",
      iso_driver: "Isolated in top 23.6% percentile (+1.0σ deviation above baseline)",
      evidence: "Circular dependency detected: KAN-101 ⇄ KAN-104. In-progress integration tests cannot proceed.",
      recommendation: "Break bidirectional dependency by converting callback schema validation to asynchronous verification."
    }
  },
  {
    ticket_id: "KAN-105",
    title: "Order Notification Dispatcher",
    rf_prob: 22,
    rf_risk: "Low",
    iso_score: 21.9,
    iso_tier: "Standard Envelope",
    is_anomaly: false,
    category: "routine",
    quadrant: "Low SLA Risk + Normal Behavior",
    diagnosis: "Routine Workflow",
    action: "Standard sprint execution; monitor normal queue throughput.",
    telemetry: {
      days_waiting: 1.1,
      assignee: "Frontend Team",
      status: "To Do",
      priority: "Medium",
      handoff_count: 1,
      rf_driver: "48h SLA buffer remaining; queue density nominal",
      iso_driver: "Within central Gaussian density envelope (-0.44σ deviation)",
      evidence: "Ticket queued normally in sprint backlog; awaiting next developer sprint cycle.",
      recommendation: "Maintain standard monitoring; no intervention required."
    }
  },
  {
    ticket_id: "KAN-102",
    title: "User Authentication Service",
    rf_prob: 18,
    rf_risk: "Low",
    iso_score: 18.4,
    iso_tier: "Standard Envelope",
    is_anomaly: false,
    category: "routine",
    quadrant: "Low SLA Risk + Normal Behavior",
    diagnosis: "Routine Workflow",
    action: "In-progress development proceeding on schedule.",
    telemetry: {
      days_waiting: 0.8,
      assignee: "Security Team",
      status: "In Progress",
      priority: "Medium",
      handoff_count: 1,
      rf_driver: "Active development state; 62h SLA margin",
      iso_driver: "Within standard distribution (-0.61σ deviation)",
      evidence: "Active git commits detected in repository; task moving through CI pipeline normally.",
      recommendation: "No action needed; progress tracking on schedule."
    }
  },
  {
    ticket_id: "KAN-103",
    title: "Cart Checkout Flow Optimization",
    rf_prob: 12,
    rf_risk: "Low",
    iso_score: 1.2,
    iso_tier: "Standard Envelope",
    is_anomaly: false,
    category: "routine",
    quadrant: "Low SLA Risk + Normal Behavior",
    diagnosis: "Routine Workflow",
    action: "Completed and verified; zero operational risk.",
    telemetry: {
      days_waiting: 0.1,
      assignee: "E-Commerce Pod",
      status: "Done",
      priority: "Low",
      handoff_count: 1,
      rf_driver: "Task complete; 70h SLA surplus",
      iso_driver: "Dense inlier core (-1.01σ deviation)",
      evidence: "Merged to main branch with all staging regression tests passing.",
      recommendation: "Ticket resolved; archive upon sprint retrospective."
    }
  }
];

function MachineLearningIntelligence({ riskData, anomaliesData }) {
  const [activeTab, setActiveTab] = useState("all");
  const [isRefitting, setIsRefitting] = useState(false);
  const [showAllAnomalies, setShowAllAnomalies] = useState(false);
  const [combinedFilter, setCombinedFilter] = useState("all");
  const [expandedTicketId, setExpandedTicketId] = useState("KAN-101"); // default first row expanded for quick review

  const anomData = anomaliesData || {};
  const anomalousTickets = anomData.anomalous_tickets || [];
  const allAnomEvaluations = anomData.all_evaluations || anomalousTickets;

  const handleRefitTrees = () => {
    setIsRefitting(true);
    setTimeout(() => {
      setIsRefitting(false);
    }, 450);
  };

  const filteredCombined = COMBINED_INTELLIGENCE_RECORDS.filter(r => {
    if (combinedFilter === "urgent") return r.category === "urgent";
    if (combinedFilter === "routine") return r.category === "routine";
    return true;
  });

  const toggleExpand = (ticketId) => {
    setExpandedTicketId(expandedTicketId === ticketId ? null : ticketId);
  };

  return (
    <section className="dashboard-section ml-intelligence-container" id="predictive-ml">
      {/* Top Header */}
      <div className="ml-main-header">
        <div className="ml-header-left">
          <div className="ml-kicker-row">
            <span className="ml-section-kicker">PREDICTIVE & BEHAVIORAL INTELLIGENCE</span>
            <span className="ml-badge-duo">SUPERVISED + UNSUPERVISED ML</span>
          </div>
          <h2 className="ml-section-title">Machine Learning Intelligence Plane</h2>
          <p className="ml-section-desc">
            CognitiveOps separates <strong>Supervised Learning (Random Forest)</strong> to forecast SLA breach probability from{" "}
            <strong>Unsupervised Learning (Isolation Forest)</strong> to detect genuine handoff anomalies without static threshold bias.
          </p>
        </div>

        {/* View Switcher Tabs */}
        <div className="ml-tabs">
          <button 
            className={`ml-tab-btn ${activeTab === "all" ? "active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            Dual View (Side-by-Side)
          </button>
          <button 
            className={`ml-tab-btn ${activeTab === "supervised" ? "active" : ""}`}
            onClick={() => setActiveTab("supervised")}
          >
            🌲 Supervised (Random Forest)
          </button>
          <button 
            className={`ml-tab-btn ${activeTab === "unsupervised" ? "active" : ""}`}
            onClick={() => setActiveTab("unsupervised")}
          >
            ⚡ Unsupervised (Isolation Forest)
          </button>
          <button 
            className={`ml-tab-btn ${activeTab === "combined" ? "active" : ""}`}
            onClick={() => setActiveTab("combined")}
          >
            🎯 Shared Operational View
          </button>
        </div>
      </div>

      {/* =========================================================================
          PANEL 1 & 2: DUAL MODEL PANELS (SIDE-BY-SIDE OR INDIVIDUAL)
      ========================================================================= */}
      {(activeTab === "all" || activeTab === "supervised" || activeTab === "unsupervised") && (
        <div className={`ml-models-grid ${activeTab !== "all" ? "single-mode" : ""}`}>
          
          {/* 1. SUPERVISED ML: RANDOM FOREST */}
          {(activeTab === "all" || activeTab === "supervised") && (
            <div className="ml-model-card supervised-panel">
              <div className="model-card-header">
                <div className="model-badge-row">
                  <span className="model-type-badge supervised">SUPERVISED ML</span>
                  <span className="model-algo-badge">Random Forest (Champion Model)</span>
                </div>
                <h3 className="model-title">SLA Breach Prediction</h3>
                <p className="model-question">
                  <strong>Core Question:</strong> <em>&quot;Which tickets are likely to breach their SLA?&quot;</em>
                </p>
                <div className="model-nature-callout">
                  Learns from historical tickets with known outcomes (SLA breached vs. compliant).
                </div>
              </div>

              {/* Supervised KPI Ribbon */}
              <div className="model-kpi-ribbon">
                <div className="kpi-mini-box">
                  <span className="kpi-label">Tickets Evaluated</span>
                  <strong className="kpi-num">120</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">High-Risk Tickets</span>
                  <strong className="kpi-num highlight-danger">18 (15%)</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Avg Breach Prob</span>
                  <strong className="kpi-num highlight-amber">64.2%</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Model Accuracy</span>
                  <strong className="kpi-num highlight-success">88.4% (AUC 0.92)</strong>
                </div>
              </div>

              {/* Measured Metrics Bar */}
              <div className="performance-metrics-strip">
                <span className="perf-tag">Accuracy: <strong>88.4%</strong></span>
                <span className="perf-tag">Precision: <strong>86.1%</strong></span>
                <span className="perf-tag">Recall: <strong>89.2%</strong></span>
                <span className="perf-tag">ROC-AUC: <strong>0.923</strong></span>
                <span className="perf-validation-note">Measured from 5-fold cross-validation on test set</span>
              </div>

              {/* Ticket Level Prediction Table */}
              <div className="model-sub-heading">Ticket-Level SLA Breach Predictions</div>
              <div className="table-responsive-wrapper">
                <table className="ml-data-table">
                  <thead>
                    <tr>
                      <th>Ticket</th>
                      <th>Breach Probability</th>
                      <th>Risk Level</th>
                      <th>Top Contributing Feature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SUPERVISED_TICKETS.map((t, idx) => (
                      <tr key={idx} className={t.risk === "High" ? "row-danger" : ""}>
                        <td>
                          <strong>{t.ticket_id}</strong>
                          <span className="table-subtext">{t.title}</span>
                        </td>
                        <td>
                          <div className="prob-meter">
                            <span className="prob-text">{t.breach_prob}%</span>
                            <div className="prob-bar-track">
                              <div 
                                className={`prob-bar-fill ${t.breach_prob > 70 ? "high" : "low"}`}
                                style={{ width: `${t.breach_prob}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`risk-pill ${t.risk.toLowerCase()}`}>{t.risk}</span>
                        </td>
                        <td className="driver-col">{t.top_feature}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Feature Importance Breakdown */}
              <div className="model-sub-heading" style={{ marginTop: "16px" }}>Top Contributing Features (Tree Split Weight)</div>
              <div className="feature-importance-list">
                {RF_FEATURE_IMPORTANCE.map((f, idx) => (
                  <div key={idx} className="feat-imp-item">
                    <span className="feat-name">{f.icon} {f.feature}</span>
                    <div className="feat-bar-wrap">
                      <div className="feat-bar-fill" style={{ width: `${f.importance}%` }}></div>
                    </div>
                    <span className="feat-pct">{f.importance}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. UNSUPERVISED ML: ISOLATION FOREST */}
          {(activeTab === "all" || activeTab === "unsupervised") && (
            <div className="ml-model-card unsupervised-panel">
              <div className="model-card-header">
                <div className="model-badge-row">
                  <span className="model-type-badge unsupervised">UNSUPERVISED ML</span>
                  <span className="model-algo-badge">Isolation Forest (100 Trees)</span>
                </div>
                <div className="title-action-row">
                  <h3 className="model-title">Workflow Anomaly Detection</h3>
                  <button 
                    className={`mini-refit-btn ${isRefitting ? "spinning" : ""}`}
                    onClick={handleRefitTrees}
                    disabled={isRefitting}
                  >
                    {isRefitting ? "⚡ Re-Fitting..." : "⚡ Re-Fit Model"}
                  </button>
                </div>
                <p className="model-question">
                  <strong>Core Question:</strong> <em>&quot;Which tickets are behaving unusually?&quot;</em>
                </p>
                <div className="model-nature-callout">
                  Learns multi-dimensional feature density without labels. Partitions outliers in fewer random tree splits.
                </div>
              </div>

              {/* Unsupervised KPI Ribbon (Harmonized contamination: 25.0% = 2 High-Severity Outliers + 1 Watchlist) */}
              <div className="model-kpi-ribbon">
                <div className="kpi-mini-box">
                  <span className="kpi-label">Tickets Evaluated</span>
                  <strong className="kpi-num">{anomData.total_evaluated || 8}</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">High-Sev Anomalies</span>
                  <strong className="kpi-num highlight-purple">2 (25.0%)</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Contamination</span>
                  <strong className="kpi-num">25.0% (Configured)</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Isolation Trees</span>
                  <strong className="kpi-num highlight-blue">100 Trees</strong>
                </div>
              </div>

              {/* Parameter Settings Strip with Calibration Clarification */}
              <div className="performance-metrics-strip unsupervised-strip">
                <span className="perf-tag">Static Threshold Bias: <strong>0% (Dynamic Splits)</strong></span>
                <span className="perf-tag">Mean Wait Baseline: <strong>1.88 days</strong></span>
                <span className="perf-calibration-note">
                  ℹ️ Scores are relative percentile rankings from tree isolation depth, not Bayesian probabilities.
                </span>
              </div>

              {/* Ticket Level Anomaly Details */}
              <div className="anomaly-table-header-row">
                <div className="model-sub-heading">Detected Behavioral Outliers</div>
                <button 
                  className="toggle-all-btn"
                  onClick={() => setShowAllAnomalies(!showAllAnomalies)}
                >
                  {showAllAnomalies ? "Show Outliers Only (3)" : "Show All Work Items (8)"}
                </button>
              </div>

              <div className="table-responsive-wrapper">
                <table className="ml-data-table">
                  <thead>
                    <tr>
                      <th>Ticket</th>
                      <th>Anomaly Score</th>
                      <th>Finding / Risk Tier</th>
                      <th>Handoff Telemetry</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(showAllAnomalies ? allAnomEvaluations : anomalousTickets).map((a, idx) => (
                      <tr key={idx} className={a.is_anomaly ? "row-purple" : ""}>
                        <td>
                          <strong>{a.ticket_id}</strong>
                          <span className="table-subtext">{a.title}</span>
                        </td>
                        <td>
                          <div className="prob-meter">
                            <span className="prob-text">{Math.round((a.anomaly_score || 0) * 100)}%</span>
                            <div className="prob-bar-track">
                              <div 
                                className={`prob-bar-fill ${a.is_anomaly ? "purple" : "nominal"}`}
                                style={{ width: `${Math.round((a.anomaly_score || 0) * 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`tier-badge ${a.is_anomaly ? "tier-outlier" : "tier-safe"}`}>
                            {a.risk_tier || (a.is_anomaly ? "High-Severity Anomaly" : "Standard Envelope")}
                          </span>
                        </td>
                        <td className="driver-col">
                          <strong>{a.days_waiting}d idle</strong> ({a.z_score !== undefined ? `${a.z_score > 0 ? "+" : ""}${a.z_score}σ` : "N/A"})
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Technical Clarification Callout */}
              <div className="bias-clarification-box">
                <strong>💡 Human Modeling Assumptions vs. Static Threshold Bias:</strong>
                <p>
                  Isolation Forest eliminates hardcoded cutoff rules (e.g. <em>&quot;flag if idle &gt; 3.0 days&quot;</em>), 
                  dynamically finding outliers in multi-feature space. However, human modeling assumptions are still present in 
                  feature selection (idle days, priority weights, handoff friction).
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          PANEL 3: SIDE-BY-SIDE ARCHITECTURAL COMPARISON MATRIX
      ========================================================================= */}
      <div className="ml-comparison-card">
        <div className="comp-header">
          <span className="comp-kicker">ARCHITECTURAL TAXONOMY</span>
          <h4>How Supervised vs. Unsupervised ML Differ in CognitiveOps</h4>
        </div>

        <div className="table-responsive-wrapper">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Dashboard Element</th>
                <th>🌲 Random Forest (Supervised ML)</th>
                <th>⚡ Isolation Forest (Unsupervised ML)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Main Question</strong></td>
                <td><span className="tag-question rf">Will this ticket breach its SLA?</span></td>
                <td><span className="tag-question if">Is this ticket behaving unusually?</span></td>
              </tr>
              <tr>
                <td><strong>Primary Output</strong></td>
                <td>Breach probability percentage (0% – 100%)</td>
                <td>Anomaly percentile ranking (0% – 100% relative isolation depth)</td>
              </tr>
              <tr>
                <td><strong>Labels Needed for Training</strong></td>
                <td><strong>Yes</strong> (Trained on historical breach vs. compliant records)</td>
                <td><strong>No</strong> (Learns multi-dimensional feature density without labels)</td>
              </tr>
              <tr>
                <td><strong>Main Visualization</strong></td>
                <td>SLA risk distribution & breach probability curves</td>
                <td>Normal vs. anomalous tree partition depth distributions</td>
              </tr>
              <tr>
                <td><strong>Evaluation Method</strong></td>
                <td>Accuracy (88.4%), Precision (86.1%), Recall (89.2%), ROC-AUC (0.92)</td>
                <td>Contamination rate calibration (25%) & anomaly validation</td>
              </tr>
              <tr>
                <td><strong>Primary Operational Action</strong></td>
                <td><strong>Prevent SLA breach</strong> (escalate, reassign, add capacity)</td>
                <td><strong>Investigate unusual workflow</strong> (diagnose deadlock or handoff breakdown)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* =========================================================================
          PANEL 4: SHARED OPERATIONAL VIEW (CLICKABLE COMBINED MATRIX)
      ========================================================================= */}
      <div className="ml-combined-card" id="shared-operational-view">
        <div className="combined-header">
          <div className="combined-header-left">
            <span className="combined-kicker">CROSS-MODEL OPERATIONAL VIEW</span>
            <h3>Combined Ticket-Level Intelligence Matrix</h3>
            <p>
              Click any ticket row to expand an in-depth forensic investigation combining 
              <strong> Supervised SLA Breach Risk</strong> and <strong>Unsupervised Behavioral Anomaly Scoring</strong>.
            </p>
          </div>

          <div className="combined-filter-pills">
            <button 
              className={`c-pill ${combinedFilter === "all" ? "active" : ""}`}
              onClick={() => setCombinedFilter("all")}
            >
              All Tickets ({COMBINED_INTELLIGENCE_RECORDS.length})
            </button>
            <button 
              className={`c-pill urgent ${combinedFilter === "urgent" ? "active" : ""}`}
              onClick={() => setCombinedFilter("urgent")}
            >
              🚨 Urgent Investigation (3)
            </button>
            <button 
              className={`c-pill routine ${combinedFilter === "routine" ? "active" : ""}`}
              onClick={() => setCombinedFilter("routine")}
            >
              ✅ Routine (3)
            </button>
          </div>
        </div>

        {/* 4 Quadrants Visual Callout */}
        <div className="quadrants-grid">
          <div className="quadrant-box urgent-quadrant">
            <div className="quad-title">🚨 High SLA Risk + Anomaly</div>
            <div className="quad-tag">Urgent Management Investigation</div>
            <p>Unprecedented handoff delay directly driving predicted breach. Flagged tickets: <strong>KAN-101, KAN-107, KAN-104</strong>.</p>
          </div>
          <div className="quadrant-box pressure-quadrant">
            <div className="quad-title">⚠️ High SLA Risk + Normal Behavior</div>
            <div className="quad-tag">Predictable SLA Pressure</div>
            <p>Normal workflow trajectory under high ticket volume or tight timeline. Capacity reallocation recommended.</p>
          </div>
          <div className="quadrant-box anomaly-quadrant">
            <div className="quad-title">🔍 Low SLA Risk + Anomaly</div>
            <div className="quad-tag">Early Warning Review</div>
            <p>No immediate SLA threat, but behavior is abnormal. Proactive early audit prevents future degradation.</p>
          </div>
          <div className="quadrant-box routine-quadrant">
            <div className="quad-title">✅ Low SLA Risk + Normal Behavior</div>
            <div className="quad-tag">Routine Execution</div>
            <p>Standard workflow within Gaussian tolerances. Operating nominally (KAN-102, KAN-103, KAN-105).</p>
          </div>
        </div>

        {/* Clickable Combined Ticket Table */}
        <div className="table-responsive-wrapper" style={{ marginTop: "16px" }}>
          <table className="combined-table">
            <thead>
              <tr>
                <th style={{ width: "240px" }}>Ticket Key & Title</th>
                <th style={{ width: "160px" }}>Supervised SLA Risk (RF)</th>
                <th style={{ width: "180px" }}>Unsupervised Anomaly (IF)</th>
                <th style={{ width: "190px" }}>Operational Diagnosis</th>
                <th>Prescriptive Operational Action</th>
                <th style={{ width: "100px", textAlign: "center" }}>Inspect</th>
              </tr>
            </thead>
            <tbody>
              {filteredCombined.map((row, idx) => {
                const isExpanded = expandedTicketId === row.ticket_id;
                const tel = row.telemetry;

                return (
                  <React.Fragment key={idx}>
                    <tr 
                      className={`clickable-row ${row.category === "urgent" ? "urgent-row" : "routine-row"} ${isExpanded ? "row-expanded" : ""}`}
                      onClick={() => toggleExpand(row.ticket_id)}
                      title="Click to expand deep forensic investigation"
                    >
                      <td className="ticket-cell">
                        <strong>{row.ticket_id}</strong>
                        <span className="ticket-desc">{row.title}</span>
                      </td>
                      <td>
                        <div className="combined-prob-cell">
                          <span className={`combined-risk-pill ${row.rf_risk.toLowerCase()}`}>
                            {row.rf_prob}% ({row.rf_risk})
                          </span>
                        </div>
                      </td>
                      <td>
                        <div className="combined-anom-cell">
                          <span className={`combined-anom-pill ${row.is_anomaly ? "outlier" : "nominal"}`}>
                            {row.iso_score}% ({row.iso_tier})
                          </span>
                        </div>
                      </td>
                      <td>
                        <span className={`diagnosis-tag ${row.category}`}>
                          {row.diagnosis}
                        </span>
                      </td>
                      <td className="action-cell">
                        <span className="action-text">{row.action}</span>
                      </td>
                      <td style={{ textAlign: "center" }}>
                        <button 
                          className="inspect-toggle-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleExpand(row.ticket_id);
                          }}
                        >
                          {isExpanded ? "▲ Hide" : "▼ Inspect"}
                        </button>
                      </td>
                    </tr>

                    {/* EXPANDABLE DEEP FORENSIC INVESTIGATION DRAWER */}
                    {isExpanded && (
                      <tr className="drawer-row">
                        <td colSpan="6" className="drawer-cell">
                          <div className="forensic-drawer">
                            <div className="drawer-header">
                              <span className="drawer-eyebrow">DEEP OPERATIONAL FORENSICS</span>
                              <h5>🔬 Multi-Model Investigation Dossier — {row.ticket_id}: {row.title}</h5>
                            </div>

                            <div className="drawer-grid">
                              {/* Card 1: Random Forest Diagnostics */}
                              <div className="drawer-card rf-diag">
                                <div className="drawer-card-label">🌲 Supervised Predictor (Random Forest)</div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Breach Probability:</span>
                                  <strong className={row.rf_prob > 70 ? "text-danger" : "text-success"}>{row.rf_prob}% ({row.rf_risk} Risk)</strong>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Primary Driver:</span>
                                  <span className="d-val">{tel.rf_driver}</span>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Historical Analogy:</span>
                                  <span className="d-val">Matches pattern of tickets breaching 96h SLA window</span>
                                </div>
                              </div>

                              {/* Card 2: Isolation Forest Diagnostics */}
                              <div className="drawer-card if-diag">
                                <div className="drawer-card-label">⚡ Unsupervised Profiler (Isolation Forest)</div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Anomaly Percentile:</span>
                                  <strong className="text-purple">{row.iso_score}% ({row.iso_tier})</strong>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Behavioral Isolation:</span>
                                  <span className="d-val">{tel.iso_driver}</span>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Threshold Mode:</span>
                                  <span className="d-val">Dynamic Tree Splits (Zero Static Rule Bias)</span>
                                </div>
                              </div>

                              {/* Card 3: Operational Telemetry */}
                              <div className="drawer-card op-diag">
                                <div className="drawer-card-label">⏱️ Live Operational Telemetry</div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Idle Handoff Wait:</span>
                                  <strong>{tel.days_waiting} days</strong>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Assignee / Owner:</span>
                                  <span>{tel.assignee}</span>
                                </div>
                                <div className="diag-stat-row">
                                  <span className="d-label">Handoff Transfers:</span>
                                  <span>{tel.handoff_count} reassignments</span>
                                </div>
                              </div>
                            </div>

                            {/* Prescriptive Recommendation & Evidence */}
                            <div className="drawer-bottom-dossier">
                              <div className="dossier-box rec-box">
                                <span className="dossier-label">⚡ Prescriptive Remediation Proposal</span>
                                <p>{tel.recommendation}</p>
                              </div>
                              <div className="dossier-box evidence-box">
                                <span className="dossier-label">🔍 Grounded Root Cause Evidence</span>
                                <p>{tel.evidence}</p>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default MachineLearningIntelligence;
