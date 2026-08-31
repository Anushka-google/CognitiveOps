import "./InsightCard.css";

function InsightCard({
  issue,
  severity,
  impact,
  recommendation,
  evidence = []
}) {
  const normalizedSeverity = String(severity ?? "Low").trim().toLowerCase();

  let severityClass = "severity-badge";

  if (normalizedSeverity === "high") {
    severityClass += " severity-high";
  } else if (normalizedSeverity === "medium") {
    severityClass += " severity-medium";
  } else {
    severityClass += " severity-low";
  }

  const evidenceItems = Array.isArray(evidence) ? evidence : [];

  return (
    <div className="insight-card">
      <h3>{issue}</h3>

      <span className={severityClass}>
        {severity || "Low"}
      </span>

      <p>
        <strong>Impact:</strong>
        {" "}
        {impact || "No impact details provided."}
      </p>

      <p>
        <strong>Recommendation:</strong>
        {" "}
        {recommendation || "No recommendation provided."}
      </p>

      {evidenceItems.length > 0 && (
        <div className="insight-evidence">
          <strong>Evidence:</strong>
          <ul>
            {evidenceItems.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default InsightCard;