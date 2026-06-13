import "./MetricCard.css";

function MetricCard({ title, value }) {

  let cardClass = "metric-card";

  if (
    title === "Workflow Health"
  ) {
    if (value === "Poor") {
      cardClass += " health-poor";
    } else if (value === "Good") {
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