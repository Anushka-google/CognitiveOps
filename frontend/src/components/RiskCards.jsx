function RiskCards({ riskData }) {

  return (
    <div className="metrics-container">

      <div className="metric-card">
        <h3>Average Risk</h3>
        <h2>{riskData.average_risk}</h2>
      </div>

      <div className="metric-card">
        <h3>High Risk Tickets</h3>
        <h2>{riskData.high_risk_tickets}</h2>
      </div>

      <div className="metric-card">
        <h3>Total Risk Tickets</h3>
        <h2>{riskData.tickets.length}</h2>
      </div>

    </div>
  );
}

export default RiskCards;