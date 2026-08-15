import { Link, useLocation } from "react-router-dom";
import "./Sidebar.css";

function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation();

  const scrollToSection = (id) => {
    const element = document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  const isDashboard = location.pathname === "/dashboard";
  const isWorkflow = location.pathname === "/workflow";

  return (
    <aside
      className={`sidebar ${
        collapsed ? "sidebar-collapsed" : ""
      }`}
    >
      {/* ================= HEADER ================= */}

      <div className="sidebar-header">
        <Link to="/" className="sidebar-brand">
          <div className="sidebar-logo">C</div>

          {!collapsed && (
            <div className="sidebar-brand-text">
              <strong>CognitiveOps</strong>
              <span>Intelligence Engine</span>
            </div>
          )}
        </Link>

        <button
          type="button"
          className="collapse-button"
          onClick={() => setCollapsed(!collapsed)}
          aria-label="Toggle sidebar"
        >
          {collapsed ? "›" : "‹"}
        </button>
      </div>

      {/* ================= NAVIGATION ================= */}

      <nav className="sidebar-navigation">

        {/* ---------- OVERVIEW ---------- */}

        {!collapsed && (
          <div className="sidebar-section-title">
            OVERVIEW
          </div>
        )}

        <button
          type="button"
          className={`sidebar-item ${
            isDashboard ? "active" : ""
          }`}
          onClick={() => scrollToSection("overview")}
          title={collapsed ? "Overview" : ""}
        >
          <span className="sidebar-icon">▦</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Overview
            </span>
          )}
        </button>

        {/* ---------- INTELLIGENCE ---------- */}

        {!collapsed && (
          <div className="sidebar-section-title">
            INTELLIGENCE
          </div>
        )}

        <button
          type="button"
          className="sidebar-item"
          onClick={() => scrollToSection("analytics")}
          title={collapsed ? "Analytics" : ""}
        >
          <span className="sidebar-icon">◈</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Analytics
            </span>
          )}
        </button>

        <button
          type="button"
          className="sidebar-item"
          onClick={() => scrollToSection("risk-analysis")}
          title={collapsed ? "Risk Analysis" : ""}
        >
          <span className="sidebar-icon">◉</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Risk Analysis
            </span>
          )}
        </button>

        <button
          type="button"
          className="sidebar-item"
          onClick={() => scrollToSection("ai-insights")}
          title={collapsed ? "AI Insights" : ""}
        >
          <span className="sidebar-icon">✦</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              AI Insights
            </span>
          )}
        </button>

        {/* ---------- WORKFLOW ---------- */}

        {!collapsed && (
          <div className="sidebar-section-title">
            WORKFLOW
          </div>
        )}

        <Link
          to="/workflow"
          className={`sidebar-item sidebar-link ${
            isWorkflow ? "active" : ""
          }`}
          title={collapsed ? "Workflow Explorer" : ""}
        >
          <span className="sidebar-icon">⌁</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Workflow Explorer
            </span>
          )}
        </Link>

      </nav>

      {/* ================= FOOTER ================= */}

      <div className="sidebar-footer">

        {/* SYSTEM STATUS */}

        <div className="sidebar-status">
          <span className="status-indicator"></span>

          {!collapsed && (
            <div className="sidebar-status-content">
              <strong>System Operational</strong>
              <span>Jira connected</span>
            </div>
          )}
        </div>

        {/* HOME */}

        <Link
          to="/"
          className="sidebar-home-link"
          title={collapsed ? "Back to Home" : ""}
        >
          <span className="sidebar-icon">←</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Back to Home
            </span>
          )}
        </Link>

      </div>
    </aside>
  );
}

export default Sidebar;