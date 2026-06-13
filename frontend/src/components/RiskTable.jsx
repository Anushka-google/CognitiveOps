function RiskTable({ riskData }) {

  return (
    <div className="insights-section">

      <h2>
        Risk Analysis
      </h2>

      <table>

        <thead>
          <tr>
            <th>Ticket ID</th>
            <th>Risk Score</th>
            <th>Risk Level</th>
            <th>Recommendation</th>
          </tr>
        </thead>

        <tbody>

          {riskData.tickets.map(
            (ticket, index) => (

              <tr key={index}>

                <td>
                  {ticket.ticket_id}
                </td>

                <td>
                  {ticket.risk_score}
                </td>

                <td
            className={
                ticket.risk_level === "High"
                    ? "high-risk"
                        : ticket.risk_level === "Medium"
                        ? "medium-risk"
                        : "low-risk"
                                }
                            >
  {ticket.risk_level}
</td>

                <td>
                  {ticket.recommendation}
                </td>

              </tr>

            )
          )}

        </tbody>

      </table>

    </div>
  );
}

export default RiskTable;