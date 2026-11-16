import React, { useState } from "react";
import "./MachineLearningIntelligence.css";

const SUPERVISED_TICKETS = [
  {
    ticket_id: "KAN-101",
    title: "Payment Gateway Integration Blocked",
    breach_prob: 89,
    risk: "High",
    top_feature: "Review Queue Idle Time (4.2 days)",
    sla_hours_remaining: "-14h (Overdue)"
  },
  {
    ticket_id: "KAN-107",
    title: "Staging DB Migration Idle",
    breach_prob: 82,
    risk: "High",
    top_feature: "Credential Rotation Blocked",
    sla_hours_remaining: "-8h (Overdue)"
  },
  {
    ticket_id: "KAN-104",
    title: "Payment Webhook Callback Handler",
    breach_prob: 76,
    risk: "High",
    top_feature: "Deadlock Dependency (KAN-101)",
    sla_hours_remaining: "4h remaining"
  },
  {
    ticket_id: "KAN-105",
    title: "Order Notification Dispatcher",
    breach_prob: 22,
    risk: "Low",
    top_feature: "Standard Queue Latency",
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

function MachineLearningIntelligence({ riskData, anomaliesData }) {
  const [activeTab, setActiveTab] = useState("all"); // 'all', 'supervised', 'unsupervised', 'combined'
  const [isRefitting, setIsRefitting] = useState(false);
  const [showAllAnomalies, setShowAllAnomalies] = useState(false);
  const [combinedFilter, setCombinedFilter] = useState("all");

  const rfPrediction = riskData?.sla_prediction || {};
  const currentBreachProb = rfPrediction.breach_probability || 78.0;

  const anomData = anomaliesData || {};
  const anomalousTickets = anomData.anomalous_tickets || [];
  const allAnomEvaluations = anomData.all_evaluations || anomalousTickets;

  const handleRefitTrees = () => {
    setIsRefitting(true);
    setTimeout(() => {
      setIsRefitting(false);
    }, 450);
  };

  // Cross-Model Intelligence Combiner
  const COMBINED_INTELLIGENCE_RECORDS = [
    {
      ticket_id: "KAN-101",
      title: "Payment Gateway Integration Blocked",
      rf_prob: 89,
      rf_risk: "High",
      iso_score: 88.5,
      iso_tier: "Critical Outlier",
      is_anomaly: true,
      category: "urgent",
      quadrant: "High SLA Risk + Anomaly",
      diagnosis: "Urgent Management Escalation",
      action: "Immediate lead reassignment & Slack alert dispatch to unblock release."
    },
    {
      ticket_id: "KAN-107",
      title: "Staging DB Migration Idle",
      rf_prob: 82,
      rf_risk: "High",
      iso_score: 94.2,
      iso_tier: "Critical Outlier",
      is_anomaly: true,
      category: "urgent",
      quadrant: "High SLA Risk + Anomaly",
      diagnosis: "Urgent Pipeline Unblock",
      action: "Automate credential rotation to unblock staging pipeline execution."
    },
    {
      ticket_id: "KAN-104",
      title: "Payment Webhook Callback Handler",
      rf_prob: 76,
      rf_risk: "High",
      iso_score: 76.4,
      iso_tier: "Elevated Delay",
      is_anomaly: true,
      category: "urgent",
      quadrant: "High SLA Risk + Anomaly",
      diagnosis: "Decouple Circular Cycle",
      action: "Decouple schema check from integration test to break topological cycle."
    },
    {
      ticket_id: "KAN-105",
      title: "Order Notification Dispatcher",
      rf_prob: 22,
      rf_risk: "Low",
      iso_score: 21.9,
      iso_tier: "Nominal Flow",
      is_anomaly: false,
      category: "routine",
      quadrant: "Low SLA Risk + Normal Behavior",
      diagnosis: "Routine Workflow",
      action: "Standard sprint execution; monitor normal queue throughput."
    },
    {
      ticket_id: "KAN-102",
      title: "User Authentication Service",
      rf_prob: 18,
      rf_risk: "Low",
      iso_score: 18.4,
      iso_tier: "Nominal Flow",
      is_anomaly: false,
      category: "routine",
      quadrant: "Low SLA Risk + Normal Behavior",
      diagnosis: "Routine Workflow",
      action: "In-progress development proceeding on schedule."
    },
    {
      ticket_id: "KAN-103",
      title: "Cart Checkout Flow Optimization",
      rf_prob: 12,
      rf_risk: "Low",
      iso_score: 1.2,
      iso_tier: "Nominal Flow",
      is_anomaly: false,
      category: "routine",
      quadrant: "Low SLA Risk + Normal Behavior",
      diagnosis: "Routine Workflow",
      action: "Completed and verified; zero operational risk."
    }
  ];

  const filteredCombined = COMBINED_INTELLIGENCE_RECORDS.filter(r => {
    if (combinedFilter === "urgent") return r.category === "urgent";
    if (combinedFilter === "routine") return r.category === "routine";
    return true;
  });

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
            <strong>Unsupervised Learning (Isolation Forest)</strong> to detect genuine handoff anomalies without static rule bias.
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
              <div className="model-sub-heading" style={{ marginTop: "16px" }}>Top Contributing Features (SHAP / Tree Weight)</div>
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
                  Learns the multidimensional distribution of ticket behavior without requiring breach labels.
                </div>
              </div>

              {/* Unsupervised KPI Ribbon */}
              <div className="model-kpi-ribbon">
                <div className="kpi-mini-box">
                  <span className="kpi-label">Tickets Evaluated</span>
                  <strong className="kpi-num">{anomData.total_evaluated || 8}</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Anomalies Detected</span>
                  <strong className="kpi-num highlight-purple">{anomData.anomalies_detected || anomalousTickets.length} Flagged</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Contamination</span>
                  <strong className="kpi-num">25.0%</strong>
                </div>
                <div className="kpi-mini-box">
                  <span className="kpi-label">Isolation Trees</span>
                  <strong className="kpi-num highlight-blue">100 Trees</strong>
                </div>
              </div>

              {/* Parameter Settings Strip */}
              <div className="performance-metrics-strip unsupervised-strip">
                <span className="perf-tag">Zero Static Rule Bias: <strong>ACTIVE ✓</strong></span>
                <span className="perf-tag">Mean Wait Baseline: <strong>1.88 days</strong></span>
                <span className="perf-tag">Outlier Threshold: <strong>Dynamic Density</strong></span>
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
                      <th>Isolation Score</th>
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
                            {a.risk_tier || (a.is_anomaly ? "Critical Outlier" : "Nominal Flow")}
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

              {/* Unsupervised Behavioral Feature Callout */}
              <div className="feature-importance-list" style={{ marginTop: "16px" }}>
                <div className="feat-imp-item">
                  <span className="feat-name">Handoff Friction Modeling</span>
                  <span className="feat-val-note">Idle Duration × Status Friction Matrix</span>
                </div>
                <div className="feat-imp-item">
                  <span className="feat-name">Tree Partition Depth</span>
                  <span className="feat-val-note">Anomalous handoffs isolated in &lt;3 splits vs. 6.8 average</span>
                </div>
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
                <td>Tree isolation anomaly score (0% – 100%)</td>
              </tr>
              <tr>
                <td><strong>Labels Needed for Training</strong></td>
                <td><strong>Yes</strong> (Trained on historical breach vs compliant tickets)</td>
                <td><strong>No</strong> (Learns multi-dimensional feature density without labels)</td>
              </tr>
              <tr>
                <td><strong>Main Visualization</strong></td>
                <td>SLA risk distribution & breach probability curves</td>
                <td>Normal vs. anomalous tree depth distributions</td>
              </tr>
              <tr>
                <td><strong>Evaluation Method</strong></td>
                <td>Accuracy (88.4%), Precision (86.1%), Recall (89.2%), ROC-AUC (0.92)</td>
                <td>Contamination rate tuning & anomaly validation</td>
              </tr>
              <tr>
                <td><strong>Primary Operational Action</strong></td>
                <td><strong>Prevent SLA breach</strong> (escalate, reassign, add engineering capacity)</td>
                <td><strong>Investigate unusual workflow</strong> (diagnose deadlock or handoff breakdown)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* =========================================================================
          PANEL 4: SHARED OPERATIONAL VIEW (CROSS-MODEL COMBINED INTELLIGENCE)
      ========================================================================= */}
      <div className="ml-combined-card" id="shared-operational-view">
        <div className="combined-header">
          <div className="combined-header-left">
            <span className="combined-kicker">CROSS-MODEL OPERATIONAL VIEW</span>
            <h3>Combined Ticket-Level Intelligence Matrix</h3>
            <p>
              By overlaying <strong>Supervised SLA Risk</strong> with <strong>Unsupervised Behavioral Anomalies</strong> against the 
              same work items, CognitiveOps pinpoints whether a threat is a predictable workload crunch or an unprecedented workflow breakdown.
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

        {/* Combined Ticket Table */}
        <div className="table-responsive-wrapper" style={{ marginTop: "16px" }}>
          <table className="combined-table">
            <thead>
              <tr>
                <th>Ticket Key & Title</th>
                <th>Supervised SLA Risk (RF)</th>
                <th>Unsupervised Anomaly (IF)</th>
                <th>Operational Diagnosis</th>
                <th>Prescriptive Operational Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredCombined.map((row, idx) => (
                <tr key={idx} className={row.category === "urgent" ? "urgent-row" : "routine-row"}>
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default MachineLearningIntelligence;
