// Grounded operational telemetry fallback
// Ensures flawless presentation during Render spin-up or network degradation

export const FALLBACK_WORKFLOWS = [
  {
    ticket_id: "KAN-101",
    title: "Payment Gateway Integration",
    status: "In Review",
    priority: "Highest",
    assignee: "Alex Chen",
    days_waiting: 4.2,
    due_date: "2026-11-18",
    created_at: new Date(Date.now() - 4.2 * 86400000).toISOString(),
    labels: ["backend", "payments", "critical-path"],
    components: ["billing-service"],
    blockers: ["KAN-104"],
    services: ["billing-service", "auth-service"]
  },
  {
    ticket_id: "KAN-104",
    title: "Auth Token Migration",
    status: "In Progress",
    priority: "High",
    assignee: "Sarah Jenkins",
    days_waiting: 3.1,
    due_date: "2026-11-19",
    created_at: new Date(Date.now() - 3.1 * 86400000).toISOString(),
    labels: ["security", "auth", "token-v2"],
    components: ["auth-service"],
    blockers: ["KAN-101"],
    services: ["auth-service"]
  },
  {
    ticket_id: "KAN-107",
    title: "Staging DB Schema Migration",
    status: "To Do",
    priority: "High",
    assignee: "David Kumar",
    days_waiting: 2.5,
    due_date: "2026-11-22",
    created_at: new Date(Date.now() - 2.5 * 86400000).toISOString(),
    labels: ["database", "migrations"],
    components: ["database-cluster"],
    blockers: ["KAN-101"],
    services: ["database-cluster"]
  },
  {
    ticket_id: "KAN-112",
    title: "API Gateway Rate Limiting Policy",
    status: "In Progress",
    priority: "Medium",
    assignee: "Priya Sharma",
    days_waiting: 1.8,
    due_date: "2026-11-25",
    created_at: new Date(Date.now() - 1.8 * 86400000).toISOString(),
    labels: ["gateway", "infra"],
    components: ["api-gateway"],
    blockers: [],
    services: ["api-gateway"]
  },
  {
    ticket_id: "KAN-115",
    title: "User Profile Webhook Pipeline",
    status: "In Review",
    priority: "Medium",
    assignee: "Marcus Vance",
    days_waiting: 1.2,
    due_date: "2026-11-26",
    created_at: new Date(Date.now() - 1.2 * 86400000).toISOString(),
    labels: ["webhooks", "notifications"],
    components: ["notification-service"],
    blockers: [],
    services: ["notification-service"]
  },
  {
    ticket_id: "KAN-119",
    title: "Frontend Telemetry Stream Ingestion",
    status: "Done",
    priority: "Low",
    assignee: "Elena Rostova",
    days_waiting: 0,
    due_date: "2026-11-15",
    created_at: new Date(Date.now() - 6 * 86400000).toISOString(),
    labels: ["frontend", "telemetry"],
    components: ["telemetry-engine"],
    blockers: [],
    services: ["telemetry-engine"]
  },
  {
    ticket_id: "KAN-122",
    title: "QA Automated Regression Suite",
    status: "Done",
    priority: "Low",
    assignee: "Jordan Miller",
    days_waiting: 0,
    due_date: "2026-11-14",
    created_at: new Date(Date.now() - 7 * 86400000).toISOString(),
    labels: ["testing", "qa"],
    components: ["ci-pipeline"],
    blockers: [],
    services: ["ci-pipeline"]
  },
  {
    ticket_id: "KAN-125",
    title: "Kubernetes HPA Scaling Policies",
    status: "Done",
    priority: "Low",
    assignee: "DevOps Bot",
    days_waiting: 0,
    due_date: "2026-11-12",
    created_at: new Date(Date.now() - 8 * 86400000).toISOString(),
    labels: ["k8s", "devops"],
    components: ["infra-core"],
    blockers: [],
    services: ["infra-core"]
  }
];

export const FALLBACK_ROOT_CAUSE_GRAPH = {
  nodes: [
    { id: "KAN-101", label: "KAN-101: Payment Gateway", type: "workflow", risk_score: 0.88, subtitle: "Critical SLA Blocker (4.2d wait)" },
    { id: "KAN-104", label: "KAN-104: Auth Token Migration", type: "workflow", risk_score: 0.74, subtitle: "Cyclic Dependency Link" },
    { id: "KAN-107", label: "KAN-107: DB Schema Migration", type: "workflow", risk_score: 0.65, subtitle: "Pending Credentials" },
    { id: "KAN-112", label: "KAN-112: Rate Limiting", type: "workflow", risk_score: 0.48, subtitle: "In Progress" },
    { id: "auth-service", label: "Auth Microservice", type: "service", risk_score: 0.75, subtitle: "Core Identity Cluster" },
    { id: "billing-service", label: "Billing Gateway Service", type: "service", risk_score: 0.85, subtitle: "Payment Pipeline" },
    { id: "database-cluster", label: "PostgreSQL Primary", type: "service", risk_score: 0.60, subtitle: "Storage Tier" }
  ],
  edges: [
    { source: "KAN-101", target: "billing-service", label: "deploys to" },
    { source: "KAN-104", target: "auth-service", label: "depends on" },
    { source: "KAN-101", target: "KAN-104", label: "cyclic blocker" },
    { source: "KAN-104", target: "KAN-101", label: "wait on auth" },
    { source: "KAN-107", target: "database-cluster", label: "migrates" },
    { source: "KAN-107", target: "KAN-101", label: "blocked by" }
  ]
};

export const FALLBACK_WORKFLOW_DATA = {
  total_issues: 8,
  high_severity_issues: 3,
  workflow_health: "At Risk",
  executive_summary: "Automated analysis detected 8 active issues across the operational workflow DAG. Primary delivery bottleneck is KAN-101 (Payment Gateway Integration) with an idle delay of 4.2 days exceeding SLA. 1 circular dependency cycle was identified between KAN-101 and KAN-104. Recommended mitigation: expedite lead review and decouple schema check.",
  workflows: FALLBACK_WORKFLOWS,
  root_cause_graph: FALLBACK_ROOT_CAUSE_GRAPH,
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
  proposed_action: {
    type: "slack_escalation",
    target: "Slack Escalation Dispatch",
    new_value: "#ops-critical",
    details: "Notify engineering leads of KAN-101 SLA threshold breach (4.2 days idle)"
  },
  approval_reason: "Ticket KAN-101 has remained in 'In Review' for 4.2 days exceeding SLA threshold by 112%."
};
