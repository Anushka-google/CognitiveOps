import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home-page">

      {/* NAVBAR */}
      <nav className="home-navbar">
        <div className="brand">
          <div className="brand-icon">C</div>
          <span>CognitiveOps</span>
        </div>

        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#platform">Platform</a>

          <Link
            to="/dashboard"
            className="nav-dashboard-btn"
          >
            Open Dashboard
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <main className="hero">

        <div className="hero-badge">
          AI-POWERED PROCESS INTELLIGENCE
        </div>

        <h1>
          Turn workflow data into
          <span> actionable intelligence.</span>
        </h1>

        <p className="hero-description">
          CognitiveOps analyzes enterprise workflows to detect
          bottlenecks, measure operational risk, and generate
          actionable AI-powered recommendations.
        </p>

        <div className="hero-actions">
          <Link
            to="/dashboard"
            className="primary-btn"
          >
            Launch Dashboard
            <span>→</span>
          </Link>

          <a
            href="#features"
            className="secondary-btn"
          >
            Explore Platform
          </a>
        </div>

        {/* PRODUCT PREVIEW */}
        <div className="product-preview">
          <div className="preview-topbar">
            <div>
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>

            <span className="preview-title">
              CognitiveOps Intelligence Console
            </span>

            <span className="live-status">
              <span></span>
              Live Analysis
            </span>
          </div>

          <div className="preview-content">

            <div className="preview-card">
              <p>WORKFLOW HEALTH</p>
              <h3>Operational Overview</h3>

              <div className="health-row">
                <span className="health-score">Poor</span>
                <span className="risk-tag">Attention Required</span>
              </div>
            </div>

            <div className="preview-card">
              <p>AI INSIGHTS</p>
              <h3>Bottleneck Detection</h3>

              <div className="insight-line">
                <span className="warning-icon">!</span>
                Approval delays detected
              </div>

              <div className="insight-line">
                <span className="success-icon">✓</span>
                Recommendations generated
              </div>
            </div>

            <div className="preview-card">
              <p>RISK INTELLIGENCE</p>
              <h3>Dynamic Risk Scoring</h3>

              <div className="risk-number">65</div>
              <span className="medium-risk">
                Medium operational risk
              </span>
            </div>

          </div>
        </div>

      </main>

      {/* FEATURES */}
      <section
        className="features-section"
        id="features"
      >
        <div className="section-heading">
          <span>PLATFORM CAPABILITIES</span>

          <h2>
            Intelligence across your workflow
          </h2>

          <p>
            From raw operational data to executive-level insights,
            CognitiveOps helps teams understand where work slows
            down and what action to take.
          </p>
        </div>

        <div className="feature-grid">

          <div className="feature-card">
            <div className="feature-number">01</div>
            <h3>Workflow Intelligence</h3>
            <p>
              Analyze Jira workflow data and identify delays,
              blockers, and operational inefficiencies automatically.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-number">02</div>
            <h3>AI Agent Analysis</h3>
            <p>
              Multi-agent orchestration analyzes workflow patterns,
              reasons about impact, and produces actionable insights.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-number">03</div>
            <h3>Dynamic Risk Scoring</h3>
            <p>
              Prioritize tickets using operational risk scores and
              quickly identify workflows requiring immediate attention.
            </p>
          </div>

        </div>
      </section>

      {/* HOW IT WORKS */}
      <section
        className="workflow-section"
        id="how-it-works"
      >
        <div className="section-heading">
          <span>HOW IT WORKS</span>
          <h2>From workflow data to decisions</h2>
        </div>

        <div className="workflow-steps">

          <div className="workflow-step">
            <span>01</span>
            <h3>Connect</h3>
            <p>
              Ingest operational workflow data from Jira.
            </p>
          </div>

          <div className="workflow-arrow">→</div>

          <div className="workflow-step">
            <span>02</span>
            <h3>Analyze</h3>
            <p>
              AI agents detect patterns, delays, and bottlenecks.
            </p>
          </div>

          <div className="workflow-arrow">→</div>

          <div className="workflow-step">
            <span>03</span>
            <h3>Prioritize</h3>
            <p>
              Risk scoring identifies the most critical issues.
            </p>
          </div>

          <div className="workflow-arrow">→</div>

          <div className="workflow-step">
            <span>04</span>
            <h3>Act</h3>
            <p>
              Receive actionable recommendations and insights.
            </p>
          </div>

        </div>
      </section>

      {/* CTA */}
      <section
        className="cta-section"
        id="platform"
      >
        <div>
          <span>COGNITIVEOPS</span>

          <h2>
            See your workflow intelligence in action.
          </h2>

          <p>
            Explore live risk analysis, bottleneck detection,
            and AI-generated operational insights.
          </p>
        </div>

        <Link
          to="/dashboard"
          className="primary-btn"
        >
          Launch Intelligence Dashboard →
        </Link>
      </section>

      <footer className="home-footer">
        <div className="brand">
          <div className="brand-icon">C</div>
          <span>CognitiveOps</span>
        </div>

        <p>
          AI-powered enterprise workflow intelligence.
        </p>
      </footer>

    </div>
  );
}

export default Home;