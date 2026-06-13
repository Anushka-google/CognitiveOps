import "./InsightCard.css";

function InsightCard({
  issue,
  severity,
  impact,
  recommendation
}) {

  let severityClass = "severity-badge";

  if (severity === "High") {
    severityClass += " severity-high";
  } else if (severity === "Medium") {
    severityClass += " severity-medium";
  } else {
    severityClass += " severity-low";
  }

  return (
    <div className="insight-card">

      <h3>{issue}</h3>

      <span className={severityClass}>
        {severity}
      </span>

      <p>
        <strong>Impact:</strong>
        {" "}
        {impact}
      </p>

      <p>
        <strong>Recommendation:</strong>
        {" "}
        {recommendation}
      </p>

    </div>
  );
}

export default InsightCard;