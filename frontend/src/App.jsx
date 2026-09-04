import {
  useEffect,
  useState,
} from "react";

import {
  getWorkflowAnalysis
} from "./services/workflowApi";

import {
  getRiskScores
} from "./services/riskApi";

import {
  getExecutionStats,
  getExecutions,
} from "./services/executionApi";

import Sidebar from "./components/Sidebar";
import MetricCard from "./components/MetricCard";
import InsightsTable from "./components/InsightsTable";
import InsightCard from "./components/InsightCard";
import IssuesChart from "./components/IssuesChart";
import WorkflowTimeline from "./components/WorkflowTimeline";
import BottleneckCard from "./components/BottleneckCard";
import SeverityPieChart from "./components/SeverityPieChart";
import RiskCards from "./components/RiskCards";
import RiskPieChart from "./components/RiskPieChart";
import RiskTable from "./components/RiskTable";
import ExecutiveSummary from "./components/ExecutiveSummary";
import ApprovalPanel from "./components/ApprovalPanel";

import "./pages/Dashboard.css";


function Dashboard() {

  const [
    data,
    setData
  ] = useState(null);

  const [
    riskData,
    setRiskData
  ] = useState(null);

  const [
    executionData,
    setExecutionData
  ] = useState([]);

  const [
    executionStats,
    setExecutionStats
  ] = useState(null);

  const [
    error,
    setError
  ] = useState(null);

  const [
    sidebarCollapsed,
    setSidebarCollapsed
  ] = useState(false);


  useEffect(() => {

    async function loadData() {

      try {

        console.log(
          "API_URL:",
          import.meta.env.VITE_API_URL
        );


        // =========================
        // WORKFLOW ANALYSIS
        // =========================

        const workflowResult =
          await getWorkflowAnalysis();

        console.log(
          "Workflow Response:",
          workflowResult
        );


        // =========================
        // RISK ANALYSIS
        // =========================

        const riskResult =
          await getRiskScores();

        console.log(
          "Risk Response:",
          riskResult
        );


        // =========================
        // EXECUTION HISTORY
        // =========================

        const executionResult =
          await getExecutions(
            0,
            20
          );

        console.log(
          "Execution Response:",
          executionResult
        );


        // =========================
        // EXECUTION STATISTICS
        // =========================

        const executionStatsResult =
          await getExecutionStats();

        console.log(
          "Execution Stats:",
          executionStatsResult
        );


        // =========================
        // SET STATE
        // =========================

        setData(
          workflowResult
        );

        setRiskData(
          riskResult
        );

        setExecutionData(
          executionResult
        );

        setExecutionStats(
          executionStatsResult
        );

      }

      catch (err) {

        console.error(
          "Dashboard loading error:",
          err
        );

        setError(
          "Unable to load workflow intelligence."
        );

      }

    }


    loadData();

  }, []);


  // =========================
  // ERROR STATE
  // =========================

  if (error) {

    return (

      <div
        className="dashboard-state-screen"
      >

        <div
          className="state-card"
        >

          <div className="state-icon">
            !
          </div>

          <h2>
            Unable to load dashboard
          </h2>

          <p>
            {error}
          </p>

          <button
            onClick={() =>
              window.location.reload()
            }
          >
            Retry
          </button>

        </div>

      </div>

    );

  }


  // =========================
  // LOADING STATE
  // =========================

  if (
    !data ||
    !riskData ||
    !data.insights ||
    !executionStats
  ) {

    return (

      <div
        className="dashboard-state-screen"
      >

        <div
          className="dashboard-loader"
        >

          <div
            className="loader-ring"
          ></div>

          <h2>
            Analyzing workflow intelligence
          </h2>

          <p>
            Processing operational data
            and calculating risk...
          </p>

        </div>

      </div>

    );

  }


  const firstInsight =
    data.insights.length > 0
      ? data.insights[0]
      : null;


  return (

    <div
      className={
        sidebarCollapsed
          ? "dashboard-page sidebar-is-collapsed"
          : "dashboard-page"
      }
    >

      {/* =========================
          SIDEBAR
      ========================= */}

      <Sidebar
        collapsed={
          sidebarCollapsed
        }

        setCollapsed={
          setSidebarCollapsed
        }
      />


      {/* =========================
          MAIN CONTENT
      ========================= */}

      <main
        className="dashboard-main"
      >

        {/* =========================
            OVERVIEW
        ========================= */}

        <section
          className="dashboard-header"
          id="overview"
        >

          <div>

            <div
              className="dashboard-eyebrow"
            >
              WORKFLOW INTELLIGENCE
            </div>

            <h1>
              Operations Overview
            </h1>

            <p>
              Monitor workflow health,
              operational risk and
              AI-generated insights.
            </p>

          </div>


          <div
            className="analysis-status"
          >

            <span
              className="analysis-dot"
            ></span>

            <div>

              <small>
                ANALYSIS STATUS
              </small>

              <strong>
                Live
              </strong>

            </div>

          </div>

        </section>


        {/* =========================
            EXECUTIVE SUMMARY
        ========================= */}

        <section
          className="dashboard-section"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                EXECUTIVE INTELLIGENCE
              </span>

              <h2>
                Executive Summary
              </h2>

            </div>

            <span
              className="ai-generated"
            >
              AI Generated
            </span>

          </div>


          <div
            className="executive-wrapper"
          >

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
                firstInsight
                  ? firstInsight.issue
                  : "No bottlenecks detected"
              }
            />

          </div>

        </section>


        {/* =========================================
            HUMAN-IN-THE-LOOP APPROVAL
        ========================================= */}

        {
          data.approval_required &&
          data.approval_status === "pending" &&
          data.proposed_action && (

            <ApprovalPanel

              proposedAction={
                data.proposed_action
              }

              approvalReason={
                data.approval_reason
              }

              onComplete={() => {

                window.location.reload();

              }}

            />

          )
        }


        {/* =========================
            KPI METRICS
        ========================= */}

        <section
          className="dashboard-section"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                KEY METRICS
              </span>

              <h2>
                Workflow Health
              </h2>

            </div>

          </div>


          <div
            className="dashboard-metrics"
          >

            <MetricCard
              title="Total Issues"
              value={
                data.total_issues
              }
            />

            <MetricCard
              title="High Severity"
              value={
                data.high_severity_issues
              }
            />

            <MetricCard
              title="Workflow Health"
              value={
                data.workflow_health
              }
            />

          </div>


          <div
            className="risk-cards-wrapper"
          >

            <RiskCards
              riskData={
                riskData
              }
            />

          </div>

        </section>


        {/* =========================
            ANALYTICS
        ========================= */}

        <section
          className="dashboard-section"
          id="analytics"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                ANALYTICS
              </span>

              <h2>
                Risk & Issue Intelligence
              </h2>

            </div>

          </div>


          <div
            className="dashboard-analytics-grid"
          >

            <div
              className="dashboard-panel"
            >

              <div
                className="panel-header"
              >

                <div>

                  <span>
                    ISSUE ANALYSIS
                  </span>

                  <h3>
                    Severity Distribution
                  </h3>

                </div>

              </div>


              <div
                className="chart-container"
              >

                <IssuesChart
                  insights={
                    data.insights
                  }
                />

              </div>

            </div>


            <div
              className="dashboard-panel"
            >

              <div
                className="panel-header"
              >

                <div>

                  <span>
                    RISK ANALYSIS
                  </span>

                  <h3>
                    Risk Distribution
                  </h3>

                </div>

              </div>


              <div
                className="chart-container"
              >

                <RiskPieChart
                  riskData={
                    riskData
                  }
                />

              </div>

            </div>

          </div>


          <div
            className="dashboard-analytics-grid second-grid"
          >

            <div
              className="dashboard-panel"
            >

              <div
                className="panel-header"
              >

                <div>

                  <span>
                    SEVERITY
                  </span>

                  <h3>
                    Severity Breakdown
                  </h3>

                </div>

              </div>


              <div
                className="chart-container"
              >

                <SeverityPieChart
                  insights={
                    data.insights
                  }
                />

              </div>

            </div>


            <div
              className="dashboard-panel bottleneck-panel"
            >

              <div
                className="panel-header"
              >

                <div>

                  <span>
                    PROCESS INTELLIGENCE
                  </span>

                  <h3>
                    Primary Bottleneck
                  </h3>

                </div>

              </div>


              <div
                className="bottleneck-wrapper"
              >

                <BottleneckCard
                  title="Top Bottleneck"

                  value={
                    firstInsight
                      ? firstInsight.issue
                      : "None detected"
                  }

                  severity={
                    firstInsight
                      ? firstInsight.severity
                      : "Low"
                  }
                />

              </div>

            </div>

          </div>

        </section>


        {/* =========================
            RISK ANALYSIS
        ========================= */}

        <section
          className="dashboard-section"
          id="risk-analysis"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                OPERATIONAL RISK
              </span>

              <h2>
                Ticket Risk Analysis
              </h2>

              <p
                className="section-description"
              >
                Prioritized workflow tickets
                based on calculated
                operational risk.
              </p>

            </div>


            <div
              className="ticket-count"
            >

              <strong>
                {
                  riskData.tickets
                    ? riskData.tickets.length
                    : 0
                }
              </strong>

              <span>
                Tickets analyzed
              </span>

            </div>

          </div>


          <div
            className="table-panel"
          >

            <RiskTable
              riskData={
                riskData
              }
            />

          </div>

        </section>


        {/* =========================
            AI INSIGHTS
        ========================= */}

        <section
          className="dashboard-section"
          id="ai-insights"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                AI INTELLIGENCE
              </span>

              <h2>
                Workflow Insights
              </h2>

              <p
                className="section-description"
              >
                Detected operational issues
                with impact analysis and
                actionable recommendations.
              </p>

            </div>


            <span
              className="insight-counter"
            >

              {data.insights.length}

              {" "}

              insight
              {
                data.insights.length !== 1
                  ? "s"
                  : ""
              }

            </span>

          </div>


          <div
            className="insights-grid"
          >

            {
              data.insights.length > 0
                ? (

                  data.insights.map(
                    (
                      insight,
                      index
                    ) => (

                      <InsightCard
                        key={
                          index
                        }

                        issue={
                          insight.issue
                        }

                        severity={
                          insight.severity
                        }

                        impact={
                          insight.impact
                        }

                        recommendation={
                          insight.recommendation
                        }

                        evidence={
                          insight.evidence
                        }
                      />

                    )
                  )

                )
                : (

                  <div
                    className="empty-insights"
                  >

                    <span>
                      ✓
                    </span>

                    <h3>
                      No critical insights
                    </h3>

                    <p>
                      No workflow bottlenecks
                      are currently detected.
                    </p>

                  </div>

                )
            }

          </div>


          <div
            className="table-panel insights-table-panel"
          >

            <InsightsTable
              insights={
                data.insights
              }
            />

          </div>

        </section>


        {/* =========================
            EXECUTION MONITORING
        ========================= */}

        <section
          className="dashboard-section"
          id="execution-history"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                EXECUTION MONITORING
              </span>

              <h2>
                Workflow Execution History
              </h2>

              <p
                className="section-description"
              >
                Historical records of
                CognitiveOps workflow
                analysis executions.
              </p>

            </div>

          </div>


          {/* =========================
              EXECUTION STATISTICS
          ========================= */}

          <div
            className="dashboard-metrics"
          >

            <MetricCard
              title="Total Executions"
              value={
                executionStats.total_executions
              }
            />

            <MetricCard
              title="Average Execution Time"
              value={
                `${executionStats.average_execution_time}s`
              }
            />

            <MetricCard
              title="Poor Executions"
              value={
                executionStats.poor_executions
              }
            />

            <MetricCard
              title="High Severity Issues"
              value={
                executionStats.total_high_severity_issues
              }
            />

          </div>


          {/* =========================
              EXECUTION TABLE
          ========================= */}

          <div
            className="table-panel"
          >

            <table>

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Health
                  </th>

                  <th>
                    Action
                  </th>

                  <th>
                    Approval
                  </th>

                  <th>
                    Execution
                  </th>

                  <th>
                    Execution Time
                  </th>

                  <th>
                    Started At
                  </th>

                </tr>

              </thead>


              <tbody>

                {
                  executionData.length > 0
                    ? (

                      executionData.map(
                        (
                          execution
                        ) => (

                          <tr
                            key={
                              execution.id
                            }
                          >

                            <td>
                              #
                              {
                                execution.id
                              }
                            </td>

                            <td>
                              {
                                execution.workflow_health
                              }
                            </td>

                            <td>
                              {
                                execution.proposed_action
                                  ? `${execution.proposed_action.target || "Unknown"} → ${execution.proposed_action.new_value || "N/A"}`
                                  : "No action"
                              }
                            </td>

                            <td>
                              {
                                execution.approval_status || "N/A"
                              }
                            </td>

                            <td>
                              {
                                execution.execution_status || "N/A"
                              }
                            </td>

                            <td>
                              {
                                execution.execution_time
                              }s
                            </td>

                            <td>
                              {
                                new Date(
                                  execution.started_at
                                ).toLocaleString()
                              }
                            </td>

                          </tr>

                        )
                      )

                    )
                    : (

                      <tr>

                        <td
                          colSpan="7"
                        >
                          No execution history found.
                        </td>

                      </tr>

                    )
                }

              </tbody>

            </table>

          </div>

        </section>


        {/* =========================
            WORKFLOW PIPELINE
        ========================= */}

        <section
          className="dashboard-section"
          id="pipeline"
        >

          <div
            className="section-label-row"
          >

            <div>

              <span
                className="section-kicker"
              >
                ANALYSIS PIPELINE
              </span>

              <h2>
                Intelligence Workflow
              </h2>

            </div>

          </div>


          <div
            className="timeline-panel"
          >

            <WorkflowTimeline />

          </div>

        </section>

      </main>


      {/* =========================
          FOOTER
      ========================= */}

      <footer
        className="dashboard-footer"
      >

        <div>

          <strong>
            CognitiveOps
          </strong>

          <span>
            AI Process Intelligence Engine
          </span>

        </div>

        <span>
          Operational Intelligence Dashboard
        </span>

      </footer>

    </div>

  );

}


export default Dashboard;