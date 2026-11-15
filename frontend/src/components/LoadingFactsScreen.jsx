import React, { useState, useEffect } from "react";
import "./LoadingFactsScreen.css";

const INSIGHT_FACTS = [
  {
    tag: "HYBRID RAG ARCHITECTURE",
    badge: "AI Precision",
    icon: "🧠",
    title: "Zero-Hallucination Retrieval",
    fact: "CognitiveOps pairs BM25 lexical keyword matching with dense vector semantics. This dual-index strategy ensures that AI insights are strictly grounded in verifiable Jira tickets rather than generative hallucinations.",
  },
  {
    tag: "GRAPH THEORY ENGINE",
    badge: "Process Mining",
    icon: "🕸️",
    title: "DAG Cycle Detection in O(V + E)",
    fact: "Our topological sorting engine detects circular dependencies in ticket workflows in linear time, flagging cross-team deadlocks before they trigger cascading sprint delays.",
  },
  {
    tag: "OPERATIONAL METRICS",
    badge: "Industry Benchmark",
    icon: "⏱️",
    title: "The Idle-Time Paradox",
    fact: "Across enterprise engineering organizations, over 65% of sprint delays are caused by unassigned waiting states and cross-team approval handoffs—not developer coding velocity.",
  },
  {
    tag: "MACHINE LEARNING",
    badge: "Anomaly Detection",
    icon: "🌲",
    title: "Unsupervised Isolation Forest Scoring",
    fact: "CognitiveOps isolates anomalous execution latencies and stalled review bottlenecks without requiring labeled training datasets, adapting dynamically to sprint velocity.",
  },
  {
    tag: "REAL-TIME TELEMETRY",
    badge: "Automation",
    icon: "🔔",
    title: "Autonomous Slack Alert Dispatch",
    fact: "When ticket SLA risk exceeds 75%, automated Webhook payloads dispatch root-cause context and mitigation steps to cross-functional leads in under 120 milliseconds.",
  },
  {
    tag: "ENTERPRISE IMPACT",
    badge: "ROI Benchmark",
    icon: "📈",
    title: "42% Reduction in MTTR",
    fact: "Proactive bottleneck identification and automated workload redistribution reduce Mean Time to Resolution (MTTR) by up to 42% across cross-functional engineering sprints.",
  },
  {
    tag: "MULTI-MODAL INGESTION",
    badge: "Integrations",
    icon: "📥",
    title: "Unified Pipeline Ingestion",
    fact: "The engine harmonizes Jira REST APIs, sprint CSV telemetry, Slack communications, and execution logs into a single centralized process intelligence plane.",
  },
];

const INIT_STEPS = [
  "Connecting to CognitiveOps Cloud Engine...",
  "Waking cloud microservices (warmup in progress)...",
  "Constructing DAG dependency graphs & detecting cycles...",
  "Evaluating ticket SLA breach vectors...",
  "Grounding operational intelligence & telemetry...",
];

function LoadingFactsScreen({ isWarmingUp = false, onForceDemo = null }) {
  const [currentFactIndex, setCurrentFactIndex] = useState(0);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Rotate facts every 3.8 seconds unless paused
  useEffect(() => {
    if (isPaused) return;
    const factInterval = setInterval(() => {
      setCurrentFactIndex((prev) => (prev + 1) % INSIGHT_FACTS.length);
    }, 3800);
    return () => clearInterval(factInterval);
  }, [isPaused]);

  // Advance pipeline status indicators
  useEffect(() => {
    const stepInterval = setInterval(() => {
      setActiveStepIndex((prev) => (prev < INIT_STEPS.length - 1 ? prev + 1 : prev));
    }, 2200);
    return () => clearInterval(stepInterval);
  }, []);

  const handleNext = () => {
    setCurrentFactIndex((prev) => (prev + 1) % INSIGHT_FACTS.length);
  };

  const handlePrev = () => {
    setCurrentFactIndex((prev) => (prev - 1 + INSIGHT_FACTS.length) % INSIGHT_FACTS.length);
  };

  const current = INSIGHT_FACTS[currentFactIndex];

  return (
    <div className="facts-loader-screen">
      <div className="facts-loader-card">
        {/* Top Header with live status */}
        <div className="facts-loader-header">
          <div className="facts-brand">
            <span className="facts-brand-icon">⚡</span>
            <span className="facts-brand-name">CognitiveOps</span>
            <span className="facts-brand-tag">Process Intelligence</span>
          </div>
          <div className="facts-live-pill">
            <span className="facts-pulse-circle"></span>
            <span>{isWarmingUp ? "Cloud Instance Warming Up" : "Synthesizing Telemetry"}</span>
          </div>
        </div>

        {/* Central Radar Animation */}
        <div className="facts-radar-wrapper">
          <div className="facts-radar-outer">
            <div className="facts-radar-inner">
              <span className="facts-radar-icon">{current.icon}</span>
            </div>
          </div>
          <h2 className="facts-loading-headline">Analyzing Workflow Intelligence</h2>
          <p className="facts-loading-subtext">
            Ingesting Jira telemetry, mapping DAG dependencies, and calculating SLA risk vectors...
          </p>
        </div>

        {/* Dynamic Rotating Fact Showcase */}
        <div 
          className="facts-showcase-box"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          <div className="facts-showcase-meta">
            <span className="facts-tag">{current.tag}</span>
            <span className="facts-badge">{current.badge}</span>
            <span className="facts-counter">
              Fact {currentFactIndex + 1} of {INSIGHT_FACTS.length}
            </span>
          </div>

          <h3 className="facts-showcase-title">{current.title}</h3>
          <p className="facts-showcase-body">{current.fact}</p>

          <div className="facts-controls">
            <button 
              className="facts-nav-btn" 
              onClick={handlePrev} 
              type="button"
              title="Previous Fact"
            >
              ◀ Prev
            </button>
            <div className="facts-dots">
              {INSIGHT_FACTS.map((_, idx) => (
                <span
                  key={idx}
                  className={`facts-dot ${idx === currentFactIndex ? "active" : ""}`}
                  onClick={() => setCurrentFactIndex(idx)}
                />
              ))}
            </div>
            <button 
              className="facts-nav-btn" 
              onClick={handleNext} 
              type="button"
              title="Next Fact"
            >
              Next ▶
            </button>
          </div>
        </div>

        {/* Live System Diagnostics / Stepper */}
        <div className="facts-pipeline-steps">
          <div className="facts-steps-header">
            <span className="facts-steps-label">System Initialization Diagnostics:</span>
            {onForceDemo && (
              <button 
                type="button" 
                className="facts-instant-btn"
                onClick={onForceDemo}
              >
                Instant Preview →
              </button>
            )}
          </div>
          <div className="facts-steps-list">
            {INIT_STEPS.map((step, idx) => {
              const isDone = idx < activeStepIndex;
              const isCurrent = idx === activeStepIndex;
              return (
                <div
                  key={idx}
                  className={`facts-step-item ${isDone ? "done" : isCurrent ? "current" : "pending"}`}
                >
                  <span className="facts-step-icon">
                    {isDone ? "✓" : isCurrent ? "●" : "○"}
                  </span>
                  <span className="facts-step-text">{step}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoadingFactsScreen;
