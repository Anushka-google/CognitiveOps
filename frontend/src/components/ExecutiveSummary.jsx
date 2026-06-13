function ExecutiveSummary({
  workflowHealth,
  totalIssues,
  highSeverity,
  bottleneck
}) {

  return (
    <div className="executive-summary">

      <h2>
        Executive Summary
      </h2>

      <p>
        Workflow health is
        <strong>
          {" "}{workflowHealth}
        </strong>.
      </p>

      <p>
        Total issues detected:
        <strong>
          {" "}{totalIssues}
        </strong>.
      </p>

      <p>
        High severity issues:
        <strong>
          {" "}{highSeverity}
        </strong>.
      </p>

      <p>
        Primary bottleneck:
        <strong>
          {" "}{bottleneck}
        </strong>.
      </p>

      <p>
        Immediate action is
        recommended.
      </p>

    </div>
  );
}

export default ExecutiveSummary;