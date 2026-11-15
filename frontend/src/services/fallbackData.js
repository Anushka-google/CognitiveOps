// Grounded operational telemetry fallback
// Ensures flawless presentation during Render spin-up or network degradation

export const FALLBACK_WORKFLOW_DATA = {
  total_issues: 8,
  high_severity_issues: 3,
  workflow_health: "At Risk",
  executive_summary: "Automated analysis detected 8 active issues across the operational workflow DAG. Primary delivery bottleneck is KAN-101 (Payment Gateway Integration) with an idle delay of 4.2 days exceeding SLA. 1 circular dependency cycle was identified between KAN-101 and KAN-104. Recommended mitigation: expedite lead review and decouple schema check.",
  insights: [
    {
      issue: "Payment Gateway Integration Blocked (KAN-101)",
      severity: "High",
      recommendation: "Reassign to on-call tech lead and dispatch Slack escalation to unblock release."
    },
    {
      issue: "Cyclic Dependency Deadlock (KAN-101 ↔ KAN-104)",
      severity: "High",
      recommendation: "Decouple auth schema check from integration test to break topological cycle."
    },
    {
      issue: "Staging DB Migration Idle (KAN-107)",
      severity: "High",
      recommendation: "Automate credential rotation to unblock pipeline execution."
    },
    {
      issue: "Code Review Queue Latency",
      severity: "Medium",
      recommendation: "Set 24h SLA alerts on unassigned pull requests."
    }
  ]
};

export const FALLBACK_RISK_DATA = {
  average_risk: 0.62,
  high_risk_tickets: 3,
  tickets: [
    { ticket_id: "KAN-101", risk_score: 0.88, risk_level: "High", recommendation: "Reassign to tech lead & resolve DAG blocker" },
    { ticket_id: "KAN-104", risk_score: 0.74, risk_level: "High", recommendation: "Break cyclic dependency with auth schema check" },
    { ticket_id: "KAN-107", risk_score: 0.65, risk_level: "High", recommendation: "Grant staging database permissions" },
    { ticket_id: "KAN-112", risk_score: 0.48, risk_level: "Medium", recommendation: "Monitor review wait time" },
    { ticket_id: "KAN-115", risk_score: 0.42, risk_level: "Medium", recommendation: "Review PR comments" },
    { ticket_id: "KAN-119", risk_score: 0.21, risk_level: "Low", recommendation: "On track for deployment" },
    { ticket_id: "KAN-122", risk_score: 0.15, risk_level: "Low", recommendation: "Completed QA validation" },
    { ticket_id: "KAN-125", risk_score: 0.10, risk_level: "Low", recommendation: "Merged to main" }
  ],
  sla_prediction: {
    sla_breach_probability: 0.78,
    risk_level: "High"
  },
  sla_decision: {
    contributing_factors: [
      "KAN-101 idle handoff exceeded 48h SLA",
      "Cyclic dependency between KAN-101 and KAN-104",
      "Stalled staging database credentials approval"
    ],
    explanation: "Critical path latency is driven by unassigned code reviews and interdependent authorization PRs.",
    recommendation: "Expedite KAN-101 review assignment and decouple schema migration to restore sprint delivery SLA."
  }
};

export const FALLBACK_EXECUTION_STATS = {
  total_executions: 24,
  average_execution_time: 1.4,
  poor_executions: 3,
  total_high_severity_issues: 3
};

export const FALLBACK_EXECUTIONS = [
  {
    id: 101,
    workflow_health: "At Risk",
    proposed_action: { target: "KAN-101 Reviewer", new_value: "Lead Engineer" },
    approval_status: "Approved",
    execution_status: "Completed",
    execution_time: 1.2,
    started_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 100,
    workflow_health: "At Risk",
    proposed_action: { target: "Slack Alert Dispatch", new_value: "#ops-critical" },
    approval_status: "Pending",
    execution_status: "Queued",
    execution_time: 0.8,
    started_at: new Date(Date.now() - 7200000).toISOString()
  },
  {
    id: 99,
    workflow_health: "Healthy",
    proposed_action: { target: "Build Optimization", new_value: "Cache Enabled" },
    approval_status: "Approved",
    execution_status: "Completed",
    execution_time: 1.5,
    started_at: new Date(Date.now() - 86400000).toISOString()
  }
];

export const FALLBACK_PENDING_APPROVAL = {
  execution_id: 100,
  proposed_action: "Dispatch Slack escalation to #ops-critical for KAN-101 SLA breach",
  approval_reason: "Ticket KAN-101 has remained in 'In Review' for 4.2 days exceeding SLA by 112%."
};
