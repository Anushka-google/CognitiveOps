import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function IssuesChart({ insights }) {

  const chartData = [
    {
      severity: "High",
      count: insights.filter(
        (item) => item.severity === "High"
      ).length,
    },
    {
      severity: "Medium",
      count: insights.filter(
        (item) => item.severity === "Medium"
      ).length,
    },
    {
      severity: "Low",
      count: insights.filter(
        (item) => item.severity === "Low"
      ).length,
    },
  ];

  return (
    <div className="chart-container">
      <h2>Issue Severity Distribution</h2>

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="severity" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="count"
            fill="#3b82f6"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default IssuesChart;