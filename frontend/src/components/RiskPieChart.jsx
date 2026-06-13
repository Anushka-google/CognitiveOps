import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

function RiskPieChart({ riskData }) {

  const data = [
    {
      name: "High",
      value: riskData.tickets.filter(
        ticket =>
          ticket.risk_level === "High"
      ).length
    },
    {
      name: "Medium",
      value: riskData.tickets.filter(
        ticket =>
          ticket.risk_level === "Medium"
      ).length
    },
    {
      name: "Low",
      value: riskData.tickets.filter(
        ticket =>
          ticket.risk_level === "Low"
      ).length
    }
  ];

  return (
    <div>
      <h2>
        Risk Distribution
      </h2>

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            label
          />
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default RiskPieChart;