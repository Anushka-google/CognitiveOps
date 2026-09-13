import { useState, useEffect } from "react";
import { getAnalyticsDashboard, downloadCsvExport } from "../services/reportsApi";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import "./AnalyticsDashboard.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isExporting, setIsExporting] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getAnalyticsDashboard();
        setMetrics(data);
      } catch (err) {
        console.error("Failed to load analytics", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleExport = async (type) => {
    setIsExporting(type);
    try {
      await downloadCsvExport(type);
    } catch (err) {
      console.error(`Failed to export ${type}`, err);
      alert(`Error exporting ${type} CSV`);
    } finally {
      setIsExporting("");
    }
  };

  if (loading) {
    return <div className="analytics-loading">Loading Historical Analytics...</div>;
  }

  if (!metrics || !metrics.trends) {
    return <div className="analytics-error">No historical data available.</div>;
  }

  const renderTrendIcon = (trend, inverted = false) => {
    // If inverted is true, negative is good (e.g. fewer bottlenecks)
    let isGood = trend > 0;
    if (inverted) isGood = trend < 0;
    if (trend === 0) return <span className="trend-neutral">− 0%</span>;
    return (
      <span className={`trend-${isGood ? "positive" : "negative"}`}>
        {trend > 0 ? "↑" : "↓"} {Math.abs(trend)}%
      </span>
    );
  };

  const MetricCard = ({ title, data, inverted }) => (
    <div className="metric-card">
      <h3 className="metric-title">{title}</h3>
      <div className="metric-value">
        <span className="current">{data.current}</span>
        <span className="unit">{data.unit}</span>
      </div>
      <div className="metric-trend">
        vs last week: {renderTrendIcon(data.trend, inverted)}
      </div>
    </div>
  );

  const chartData = {
    labels: metrics.trends.dates,
    datasets: [
      {
        label: 'Overall Health Score',
        data: metrics.trends.history,
        borderColor: '#58a6ff',
        backgroundColor: 'rgba(88, 166, 255, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#161b22',
        titleColor: '#c9d1d9',
        bodyColor: '#c9d1d9',
        borderColor: '#30363d',
        borderWidth: 1
      }
    },
    scales: {
      y: {
        grid: { color: '#30363d' },
        ticks: { color: '#8b949e' },
        min: 0,
        max: 100
      },
      x: {
        grid: { display: false },
        ticks: { color: '#8b949e', maxTicksLimit: 7 }
      }
    }
  };

  return (
    <div className="analytics-container">
      
      {/* EXPORT DATA CENTER */}
      <div className="export-center">
        <h3>Export Data (CSV)</h3>
        <div className="export-buttons">
          <button className="export-btn" onClick={() => handleExport('workflows')} disabled={isExporting !== ""}>
            {isExporting === 'workflows' ? "Exporting..." : "↓ Workflows"}
          </button>
          <button className="export-btn" onClick={() => handleExport('risks')} disabled={isExporting !== ""}>
            {isExporting === 'risks' ? "Exporting..." : "↓ Risks"}
          </button>
          <button className="export-btn" onClick={() => handleExport('insights')} disabled={isExporting !== ""}>
            {isExporting === 'insights' ? "Exporting..." : "↓ Insights"}
          </button>
          <button className="export-btn" onClick={() => handleExport('recommendations')} disabled={isExporting !== ""}>
            {isExporting === 'recommendations' ? "Exporting..." : "↓ Recommendations"}
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard title="Avg Duration" data={metrics.duration} inverted={true} />
        <MetricCard title="Active Bottlenecks" data={metrics.bottlenecks} inverted={true} />
        <MetricCard title="High Risk Items" data={metrics.risk} inverted={true} />
        <MetricCard title="SLA Breach Rate" data={metrics.sla} inverted={true} />
        <MetricCard title="Team Velocity" data={metrics.team_performance} inverted={false} />
      </div>

      <div className="trends-chart-container">
        <div className="chart-header">
          <h3>Workflow Health Trends (Last 30 Days)</h3>
          <div className="chart-meta">
            <span className="current-score">{metrics.trends.current} / 100</span>
            {renderTrendIcon(metrics.trends.trend)}
          </div>
        </div>
        <div className="chart-wrapper">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
