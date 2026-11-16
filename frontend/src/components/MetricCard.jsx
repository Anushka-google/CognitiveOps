import "./MetricCard.css";

function MetricCard({
  title,
  value
}) {
  let cardClass = "metric-card";

  if (title === "Workflow Health") {
    if (value === "Poor" || String(value).toLowerCase().includes("risk")) {
      cardClass += " health-poor";
    } else if (value === "Good" || String(value).toLowerCase().includes("health")) {
      cardClass += " health-good";
    }
  }

  if (title === "SLA Risk") {
    if (value === "High") {
      cardClass += " health-poor";
    } else if (value === "Medium") {
      cardClass += " risk-medium";
    } else if (value === "Low") {
      cardClass += " health-good";
    }
  }

  return (
    <div className={cardClass}>
      <h2>{title}</h2>
      <p>{value}</p>
    </div>
  );
}

export default MetricCard;
