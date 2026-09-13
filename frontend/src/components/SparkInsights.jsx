import { useState } from "react";
import "./SparkInsights.css";

const API_URL = import.meta.env.VITE_API_URL;

function SparkInsights() {
  const [data, setData] = useState(null);
  const [stages, setStages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runFullETL = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/reports/spark-etl`);
      const result = await response.json();
      if (result.status === "success") {
        setData(result.data);
        setStages(result.pipeline_stages);
      } else {
        setError(result.message || "Failed to execute PySpark ETL pipeline");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="spark-wrapper">
      <div className="spark-container">
        <div className="spark-header">
          <div className="spark-title">
            <span className="spark-icon">⚡</span>
            <h3>Phase 7: Complete PySpark ETL Pipeline</h3>
          </div>
          <button className="spark-refresh-btn" onClick={runFullETL} disabled={loading}>
            {loading ? "Executing Pipeline..." : "Run End-to-End ETL"}
          </button>
        </div>
        
        <p className="spark-description">
          Executes the complete Big Data pipeline: Extract → Clean (drop duplicates/nulls) → Feature Transform → Aggregate → Load to PostgreSQL.
        </p>

        {error && <div className="spark-error">{error}</div>}

        {stages && !loading && (
          <div className="spark-stages">
            <h4>ETL Pipeline Execution Log</h4>
            <div className="stages-grid">
              {stages.map((stage, idx) => (
                <div key={idx} className="stage-card">
                  <div className="stage-badge">{idx + 1}</div>
                  <h5>{stage.stage}</h5>
                  <pre>{JSON.stringify(stage, null, 2).replace(/"stage": ".*",?\n?/, '')}</pre>
                </div>
              ))}
            </div>
          </div>
        )}

        {data && !loading && (
          <div className="spark-table-container" style={{ marginTop: '24px' }}>
            <table className="spark-table">
              <thead>
                <tr>
                  <th>Team / Assignee</th>
                  <th>Total Workflows</th>
                  <th>Avg Waiting (Days)</th>
                  <th>Blocker Density</th>
                  <th>High-Risk Workflows</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, index) => (
                  <tr key={index}>
                    <td>{row.team_name || row.assignee || "Unknown"}</td>
                    <td>{row.total_workflows}</td>
                    <td>{row.avg_waiting_time}</td>
                    <td>{(row.blocker_density * 100).toFixed(0)}%</td>
                    <td>{row.high_risk_workflows}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default SparkInsights;
