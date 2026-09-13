import { useState, useEffect } from "react";
import { getJiraStatus, testJiraConnection, getSlackStatus, testSlackConnection } from "../services/integrationApi";
import "./Integrations.css";

function Integrations() {
  const [jiraStatus, setJiraStatus] = useState(null);
  const [slackStatus, setSlackStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState({ type: "", message: "" });
  
  // Modal State
  const [activeModal, setActiveModal] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    async function loadStatuses() {
      try {
        const [jira, slack] = await Promise.all([
          getJiraStatus().catch(() => null),
          getSlackStatus().catch(() => null)
        ]);
        setJiraStatus(jira);
        setSlackStatus(slack);
      } catch (err) {
        console.error("Failed to load integrations", err);
      } finally {
        setLoading(false);
      }
    }
    loadStatuses();
  }, []);

  const handleTestJira = async () => {
    setTestResult({ type: "info", message: "Testing Jira connection..." });
    try {
      const res = await testJiraConnection();
      if (res && res.error) {
        setTestResult({ type: "error", message: `Jira: ${res.error}` });
      } else {
        setTestResult({ type: "success", message: "Jira connected successfully!" });
      }
    } catch (err) {
      setTestResult({ type: "error", message: "Jira connection failed." });
    }
  };

  const handleTestSlack = async () => {
    setTestResult({ type: "info", message: "Testing Slack connection..." });
    try {
      const res = await testSlackConnection();
      if (res.success) {
        setTestResult({ type: "success", message: res.message });
      } else {
        setTestResult({ type: "error", message: res.message });
      }
    } catch (err) {
      setTestResult({ type: "error", message: "Slack connection failed." });
    }
  };

  const handleSaveConfiguration = (e) => {
    e.preventDefault();
    setIsSaving(true);
    // Mocking an API call to save configurations to the DB
    setTimeout(() => {
      setIsSaving(false);
      setActiveModal(null);
      setTestResult({ type: "success", message: `${activeModal.toUpperCase()} configuration saved successfully!`});
    }, 1000);
  };

  if (loading) {
    return <div className="integrations-loading">Loading integrations...</div>;
  }

  const isJiraConnected = jiraStatus?.token_exists && jiraStatus?.email_exists;
  const isSlackConnected = slackStatus?.connected;

  return (
    <main className="integrations-page">
      <div className="integrations-header">
        <h1>Integrations</h1>
        <p>Manage your connected workspace tools and platforms.</p>
      </div>

      {testResult.message && (
        <div className={`integration-alert alert-${testResult.type}`}>
          {testResult.message}
        </div>
      )}

      <div className="integrations-grid">
        {/* JIRA CARD */}
        <div className="integration-card">
          <div className="integration-card-header">
            <div className="integration-icon jira-icon">J</div>
            <div className="integration-title">
              <h2>Jira Software</h2>
              <span className={`status-badge ${isJiraConnected ? "connected" : "disconnected"}`}>
                {isJiraConnected ? "Connected" : "Not Connected"}
              </span>
            </div>
          </div>
          
          <div className="integration-body">
            <p className="integration-desc">Connect Jira to analyze workflow bottlenecks, track tickets, and predict SLA breaches.</p>
            <div className="integration-config">
              <div className="config-item">
                <span className="config-label">Base URL:</span>
                <span className="config-value">{jiraStatus?.base_url || "Not configured"}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Project Key:</span>
                <span className="config-value">{jiraStatus?.project_key || "Not configured"}</span>
              </div>
            </div>
          </div>
          
          <div className="integration-footer">
            <button className="test-btn" onClick={handleTestJira}>Test Connection</button>
            <button className="config-btn" onClick={() => setActiveModal('jira')}>Configure</button>
          </div>
        </div>

        {/* SLACK CARD */}
        <div className="integration-card">
          <div className="integration-card-header">
            <div className="integration-icon slack-icon">S</div>
            <div className="integration-title">
              <h2>Slack</h2>
              <span className={`status-badge ${isSlackConnected ? "connected" : "disconnected"}`}>
                {isSlackConnected ? "Connected" : "Not Connected"}
              </span>
            </div>
          </div>
          
          <div className="integration-body">
            <p className="integration-desc">Connect Slack to receive automated bottleneck alerts and executive reports directly in your channels.</p>
            <div className="integration-config">
              <div className="config-item">
                <span className="config-label">Webhook:</span>
                <span className="config-value">{slackStatus?.details?.webhook_configured ? "Configured" : "Missing"}</span>
              </div>
              <div className="config-item">
                <span className="config-label">API Token:</span>
                <span className="config-value">{slackStatus?.details?.api_token_configured ? "Configured" : "Missing"}</span>
              </div>
            </div>
          </div>
          
          <div className="integration-footer">
            <button className="test-btn" onClick={handleTestSlack}>Test Connection</button>
            <button className="config-btn" onClick={() => setActiveModal('slack')}>Configure</button>
          </div>
        </div>
      </div>

      {/* CONFIGURATION MODAL */}
      {activeModal && (
        <div className="integration-modal-overlay">
          <div className="integration-modal">
            <div className="modal-header">
              <h3>Configure {activeModal === 'jira' ? 'Jira' : 'Slack'}</h3>
              <button className="modal-close" onClick={() => setActiveModal(null)}>&times;</button>
            </div>
            
            <form onSubmit={handleSaveConfiguration} className="modal-body">
              {activeModal === 'jira' && (
                <>
                  <div className="form-group">
                    <label>Base URL</label>
                    <input type="text" placeholder="e.g. https://your-domain.atlassian.net" defaultValue={jiraStatus?.base_url || ''} required />
                  </div>
                  <div className="form-group">
                    <label>Jira Email</label>
                    <input type="email" placeholder="e.g. you@company.com" required />
                  </div>
                  <div className="form-group">
                    <label>Project Key</label>
                    <input type="text" placeholder="e.g. KAN" defaultValue={jiraStatus?.project_key || ''} required />
                  </div>
                  <div className="form-group">
                    <label>API Token</label>
                    <input type="password" placeholder="Paste your Jira API token" required />
                  </div>
                </>
              )}

              {activeModal === 'slack' && (
                <>
                  <div className="form-group">
                    <label>Incoming Webhook URL</label>
                    <input type="url" placeholder="https://hooks.slack.com/services/..." />
                  </div>
                  <div className="form-group">
                    <label>Bot User OAuth Token</label>
                    <input type="password" placeholder="xoxb-your-token" />
                  </div>
                </>
              )}

              <div className="modal-footer">
                <button type="button" className="btn-cancel" onClick={() => setActiveModal(null)}>Cancel</button>
                <button type="submit" className="btn-save" disabled={isSaving}>
                  {isSaving ? "Saving..." : "Save Configuration"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </main>
  );
}

export default Integrations;
