import "./InsightsTable.css";
function InsightsTable({ insights }) {

  return (
  <div className="table-container">

    <table>

      <thead>
        <tr>
          <th>Issue</th>
          <th>Severity</th>
        </tr>
      </thead>

      <tbody>

        {insights.map(
          (insight, index) => (
            <tr key={index}>
              <td>{insight.issue}</td>

              <td>
                <span
                  className={`severity-badge severity-${insight.severity.toLowerCase()}`}
                >
                  {insight.severity}
                </span>
              </td>
            </tr>
          )
        )}

      </tbody>

    </table>

  </div>
);
}

export default InsightsTable;