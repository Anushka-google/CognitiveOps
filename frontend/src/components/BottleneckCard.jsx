import "./BottleneckCard.css";
function BottleneckCard({
  title,
  value,
  severity
}) {
  return (
    <div className="bottleneck-card">
      <h3>{title}</h3>

      <h2>{value}</h2>

      <span>
        Severity: {severity}
      </span>
    </div>
  );
}

export default BottleneckCard;