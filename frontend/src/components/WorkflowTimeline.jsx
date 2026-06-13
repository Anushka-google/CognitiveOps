import "./WorkflowTimeline.css";
function WorkflowTimeline() {
  const steps = [
    "Upload Workflow",
    "Parse Workflow",
    "Analyze Issues",
    "Generate Insights",
    "Dashboard Report",
  ];

  return (
    <div className="timeline-container">
      <h2>Workflow Timeline</h2>

      {steps.map((step, index) => (
        <div
          key={index}
          className="timeline-step"
        >
          <div className="timeline-circle">
            {index + 1}
          </div>

          <div className="timeline-content">
            {step}
          </div>
        </div>
      ))}
    </div>
  );
}

export default WorkflowTimeline;