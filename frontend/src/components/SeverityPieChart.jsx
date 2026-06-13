import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

function SeverityPieChart({ insights }) {

  const high = insights.filter(
    (item) => item.severity === "High"
  ).length;

  const medium = insights.filter(
    (item) => item.severity === "Medium"
  ).length;

  const low = insights.filter(
    (item) => item.severity === "Low"
  ).length;

  const data = [
    { name: "High", value: high },
    { name: "Medium", value: medium },
    { name: "Low", value: low }
  ];

  const COLORS = [
    "#ef4444",
    "#f59e0b",
    "#22c55e"
  ];

  return (
    <div className="chart-container">
      <h2>Severity Breakdown</h2>

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            outerRadius={100}
            label
          >
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={COLORS[index]}
              />
            ))}
          </Pie>

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SeverityPieChart;