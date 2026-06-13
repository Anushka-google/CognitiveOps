import { useEffect, useState } from "react";
import { getWorkflowAnalysis } from "../services/workflowApi";
import MetricCard from "../components/MetricCard";
import InsightsTable from "../components/InsightsTable";
import InsightCard from "../components/InsightCard";
import "./Dashboard.css";
import IssuesChart from "../components/IssuesChart";
import WorkflowTimeline from "../components/WorkflowTimeline";
import BottleneckCard from "../components/BottleneckCard";
import SeverityPieChart from "../components/SeverityPieChart";
import { getRiskScores }
from "../services/riskApi";
import RiskCards
from "../components/RiskCards";
import RiskPieChart
from "../components/RiskPieChart";
import RiskTable
from "../components/RiskTable";
import ExecutiveSummary
from "../components/ExecutiveSummary";







function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [riskData, setRiskData] = useState(null);
  useEffect(() => {
    async function loadData() {
      try {
        const result = await getWorkflowAnalysis();
        setData(result);
        const riskResult = await getRiskScores();
        setRiskData(riskResult);
      } catch (error) {
        setError("Failed to load Dashboard data");
        console.error("Error loading data:", error);
      }
    }

    loadData();
  }, []);

  if (error) {
    return <h2>{error}</h2>;
  }

  if (
  !data ||
  !riskData
) {
  return (
    <div className="loading-screen">
      Loading Dashboard...
    </div>
  );
}

  return (
    <div className="dashboard">
      <h1>CognitiveOps Dashboard</h1>

      <ExecutiveSummary
  workflowHealth={
    data.workflow_health
  }
  totalIssues={
    data.total_issues
  }
  highSeverity={
    data.high_severity_issues
  }
  bottleneck={
    data.insights[0].issue
  }
/>

      <div className="metrics-container">
        <MetricCard
          title="Total Issues"
          value={data.total_issues}
        />

        <MetricCard
          title="High Severity Issues"
          value={data.high_severity_issues}
        />

        <MetricCard
          title="Workflow Health"
          value={data.workflow_health}
        />
      </div>
        <RiskCards
        riskData={riskData}
        />
      <div className="analytics-grid">

  <div className="analytics-card">
    <IssuesChart
      insights={data.insights}
    />
  </div>

  <div className="analytics-card">
    <RiskPieChart
      riskData={riskData}
    />
  </div>

</div>

<div className="analytics-grid">

  <div className="analytics-card">
    <SeverityPieChart
      insights={data.insights}
    />
  </div>

  <div className="analytics-card">
    <BottleneckCard
      title="Top Bottleneck"
      value={data.insights[0].issue}
      severity={data.insights[0].severity}
    />
  </div>

</div>

<RiskTable
  riskData={riskData}
/>

      <div className="insights-section">
  <h2>Workflow Insights</h2>

  {data.insights.map((insight, index) => (
    <InsightCard
      key={index}
      issue={insight.issue}
      severity={insight.severity}
      impact={insight.impact}
      recommendation={insight.recommendation}
    />
  ))}

  <InsightsTable
    insights={data.insights}
  />
  <WorkflowTimeline />
</div>
    </div>
  );
}

export default Dashboard;