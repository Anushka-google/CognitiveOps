import { Link } from "react-router-dom";
import "./Sidebar.css";

function Sidebar({
  collapsed,
  setCollapsed,
}) {

  const scrollToSection = (id) => {

    const element =
      document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  return (
    <aside
      className={
        collapsed
          ? "sidebar sidebar-collapsed"
          : "sidebar"
      }
    >

      {/* LOGO */}

      <div className="sidebar-header">

        <Link
          to="/"
          className="sidebar-brand"
        >
          <div className="sidebar-logo">
            C
          </div>

          {!collapsed && (
            <div className="sidebar-brand-text">
              <strong>
                CognitiveOps
              </strong>

              <span>
                Intelligence Engine
              </span>
            </div>
          )}

        </Link>

        <button
          className="collapse-button"
          onClick={() =>
            setCollapsed(
              !collapsed
            )
          }
          aria-label="Toggle sidebar"
        >
          {collapsed ? "›" : "‹"}
        </button>

      </div>


      {/* NAVIGATION */}

      <nav className="sidebar-navigation">

        {!collapsed && (
          <span className="sidebar-section-title">
            OVERVIEW
          </span>
        )}

        <button
          className="sidebar-item active"
          onClick={() =>
            scrollToSection(
              "overview"
            )
          }
        >
          <span className="sidebar-icon">
            ▦
          </span>

          {!collapsed && (
            <span>Overview</span>
          )}
        </button>


        {!collapsed && (
          <span className="sidebar-section-title">
            INTELLIGENCE
          </span>
        )}

        <button
          className="sidebar-item"
          onClick={() =>
            scrollToSection(
              "analytics"
            )
          }
        >
          <span className="sidebar-icon">
            ◈
          </span>

          {!collapsed && (
            <span>Analytics</span>
          )}
        </button>


        <button
          className="sidebar-item"
          onClick={() =>
            scrollToSection(
              "risk-analysis"
            )
          }
        >
          <span className="sidebar-icon">
            ◉
          </span>

          {!collapsed && (
            <span>
              Risk Analysis
            </span>
          )}
        </button>


        <button
          className="sidebar-item"
          onClick={() =>
            scrollToSection(
              "ai-insights"
            )
          }
        >
          <span className="sidebar-icon">
            ✦
          </span>

          {!collapsed && (
            <span>
              AI Insights
            </span>
          )}
        </button>


        {!collapsed && (
          <span className="sidebar-section-title">
            WORKFLOW
          </span>
        )}

        <button
          className="sidebar-item"
          onClick={() =>
            scrollToSection(
              "pipeline"
            )
          }
        >
          <span className="sidebar-icon">
            ⌁
          </span>

          {!collapsed && (
            <span>
              Analysis Pipeline
            </span>
          )}
        </button>

      </nav>


      {/* BOTTOM */}

      <div className="sidebar-footer">

        <div className="sidebar-status">

          <span className="status-indicator">
          </span>

          {!collapsed && (
            <div>
              <strong>
                System Operational
              </strong>

              <span>
                Jira connected
              </span>
            </div>
          )}

        </div>

        <Link
          to="/"
          className="sidebar-home-link"
        >

          <span className="sidebar-icon">
            ←
          </span>

          {!collapsed && (
            <span>
              Back to Home
            </span>
          )}

        </Link>

      </div>

    </aside>
  );
}

export default Sidebar;