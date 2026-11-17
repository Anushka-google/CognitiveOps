import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

function Sidebar({ collapsed, setCollapsed }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const isDashboard = location.pathname === "/" || location.pathname === "/dashboard";
  const isWorkflow = location.pathname === "/workflow";
  const isChat = location.pathname === "/chat";
  const isIntegrations = location.pathname === "/integrations";

  const handleNavigateSection = (id) => {
    if (isDashboard) {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    } else {
      // Navigate to Dashboard with target hash so App.jsx auto-scrolls to the section
      navigate(`/#${id}`);
    }
  };

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

        {setCollapsed && (
          <button
            type="button"
            className="collapse-button"
            onClick={() => setCollapsed(!collapsed)}
            aria-label="Toggle sidebar"
          >
            {collapsed ? "›" : "‹"}
          </button>
        )}
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
          onClick={() => handleNavigateSection("overview")}
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
          onClick={() => handleNavigateSection("analytics")}
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
          onClick={() => handleNavigateSection("risk-analysis")}
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
          onClick={() => handleNavigateSection("ai-insights")}
          title={collapsed ? "AI Insights" : ""}
        >
          <span className="sidebar-icon">✦</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              AI Insights
            </span>
          )}
        </button>

        <button
          type="button"
          className="sidebar-item"
          onClick={() => handleNavigateSection("pipeline")}
          title={collapsed ? "5-Stage Pipeline" : ""}
        >
          <span className="sidebar-icon">⚡</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              5-Stage Pipeline
            </span>
          )}
        </button>

        <button
          type="button"
          className="sidebar-item"
          onClick={() => handleNavigateSection("predictive-ml")}
          title={collapsed ? "ML Intelligence" : ""}
        >
          <span className="sidebar-icon">🌲</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              ML Intelligence
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

        <Link
          to="/chat"
          className={`sidebar-item sidebar-link ${
            isChat ? "active" : ""
          }`}
          title={collapsed ? "AI Chat" : ""}
        >
          <span className="sidebar-icon">🤖</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              AI Chat
            </span>
          )}
        </Link>

        <Link
          to="/integrations"
          className={`sidebar-item sidebar-link ${
            isIntegrations ? "active" : ""
          }`}
          title={collapsed ? "Integrations" : ""}
        >
          <span className="sidebar-icon">🔌</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Integrations
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

        {/* LOGOUT */}

        <button
          onClick={logout}
          className="sidebar-home-link"
          style={{ background: 'none', border: 'none', width: '100%', textAlign: 'left', cursor: 'pointer' }}
          title={collapsed ? "Logout" : ""}
        >
          <span className="sidebar-icon">🚪</span>

          {!collapsed && (
            <span className="sidebar-item-text">
              Logout
            </span>
          )}
        </button>

      </div>
    </aside>
  );
}

export default Sidebar;