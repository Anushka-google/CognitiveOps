import { useState, useEffect } from "react";
import "./SparkInsights.css";

const API_URL = import.meta.env.VITE_API_URL;

function SparkInsights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSparkData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/reports/spark-insights`);
      const result = await response.json();
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.error || "Failed to fetch Spark insights");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSparkData();
  }, []);

  return (
    <div className="spark-container">
      <div className="spark-header">
        <div className="spark-title">
          <span className="spark-icon">⚡</span>
          <h3>PySpark Big Data Engine</h3>
        </div>
        <button className="spark-refresh-btn" onClick={fetchSparkData} disabled={loading}>
          {loading ? "Processing..." : "Run Spark Job"}
        </button>
      </div>
      
      <p className="spark-description">
        Distributed DataFrames compute team SLA breaches and bottleneck aggregations across the entire historical data lake.
      </p>

      {error && <div className="spark-error">{error}</div>}

      {data && !loading && (
        <div className="spark-grid">
          {data.map((team, index) => (
            <div key={index} className="spark-card">
              <div className="spark-card-header">
                <h4>{team.team_name}</h4>
                <span className="spark-region">{team.region}</span>
              </div>
              <div className="spark-metrics">
                <div className="spark-metric">
                  <span className="spark-value">{team.active_workflows}</span>
                  <span className="spark-label">Active Workflows</span>
                </div>
                <div className="spark-metric">
                  <span className="spark-value">{team.avg_days_waiting.toFixed(1)}</span>
                  <span className="spark-label">Avg Wait (Days)</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SparkInsights;
