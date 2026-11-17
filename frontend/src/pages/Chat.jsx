import React, { useState, useEffect, useRef } from "react";
import { askChat } from "../services/chatApi";
import "./Chat.css";

const THINKING_PHRASES = [
  "🧠 Ingesting query into Hybrid RAG engine...",
  "🕸️ Checking DAG dependency graph for circular blockers...",
  "📊 Correlating Jira ticket SLA breach vectors...",
  "⚡ Synthesizing grounded operational intelligence...",
];

const SUGGESTED_QUERIES = [
  { label: "Why is the workflow delayed?", icon: "⚡" },
  { label: "Find the biggest bottleneck.", icon: "🔍" },
  { label: "What action should we take?", icon: "🛡️" },
  { label: "Check circular deadlock cycles in KAN-101.", icon: "🕸️" },
];

function formatMessageContent(content) {
  if (typeof content !== "string") return content;
  return content.split("\n").map((line, lineIdx) => {
    const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);
    return (
      <React.Fragment key={lineIdx}>
        {parts.map((part, pIdx) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return <strong key={pIdx}>{part.slice(2, -2)}</strong>;
          }
          if (part.startsWith("*") && part.endsWith("*")) {
            return <em key={pIdx}>{part.slice(1, -1)}</em>;
          }
          return part;
        })}
        {lineIdx < content.split("\n").length - 1 && <br />}
      </React.Fragment>
    );
  });
}

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [thinkingIndex, setThinkingIndex] = useState(0);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Cycle thinking phrases while loading
  useEffect(() => {
    if (!loading) {
      setThinkingIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setThinkingIndex((prev) => (prev + 1) % THINKING_PHRASES.length);
    }, 1800);
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (event) => {
    if (event) event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await askChat(trimmedQuestion);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            response.answer ||
            "I could not generate an answer.",
          evidence: response.evidence || [],
          citations: response.citations || [],
          confidence: response.confidence,
          recommendations:
            response.recommendations || [],
          insufficientEvidence:
            response.insufficient_evidence || false,
          offlineFallback: response.offline_fallback || false,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error.message || "Unable to process the request right now.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (promptText) => {
    setQuestion(promptText);
  };

  return (
    <main className="chat-page">
      {/* ================= HEADER ================= */}
      <div className="chat-header">
        <div className="chat-header-main">
          <div className="chat-eyebrow">
            <span className="brand-dot">⚡</span> NEURAL OPS INTELLIGENCE • HYBRID RAG AGENT
          </div>
          <h1>CognitiveOps Intelligence Chat</h1>
          <p>
            Autonomous root cause correlation across Jira blockers, SLA vectors, and DAG dependencies.
          </p>
        </div>

        <div className="chat-hud-telemetry">
          <div className="chat-telemetry-badge active">
            <span className="status-dot"></span>
            <span>RAG ENGINE // LIVE</span>
          </div>
          <div className="chat-telemetry-badge">
            <span className="mono-label">MODEL:</span>
            <span>GEMINI EMBEDDING</span>
          </div>
          <div className="chat-telemetry-badge">
            <span className="mono-label">ZERO-HALLUCINATION:</span>
            <span className="emerald">ACTIVE</span>
          </div>
        </div>
      </div>

      {/* ================= CHAT CONSOLE ================= */}
      <section className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <div className="chat-empty-icon">🤖</div>
              <h2>Operational Intelligence Console</h2>
              <p>
                Query root causes, predict SLA impacts, or ask the AI to recommend automated mitigation workflows.
              </p>

              <div className="chat-examples">
                {SUGGESTED_QUERIES.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleQuickPrompt(item.label)}
                  >
                    <span>{item.icon}</span> {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`chat-message ${message.role}`}
            >
              <div className="chat-message-label">
                <span className="sender-avatar">
                  {message.role === "user" ? "OP" : "⚡"}
                </span>
                {message.role === "user"
                  ? "Incident Commander"
                  : "CognitiveOps Neural Agent"}
                {message.offlineFallback && (
                  <span className="grounded-telemetry-pill">
                    ⚡ Grounded Telemetry
                  </span>
                )}
              </div>

              {message.error ? (
                <div className="chat-error">
                  {message.content}
                </div>
              ) : (
                <div className="chat-message-content">
                  {formatMessageContent(message.content)}
                </div>
              )}

              {message.role === "assistant" &&
                !message.error && (
                  <div className="chat-metadata-deck">
                    {message.insufficientEvidence && (
                      <div className="chat-warning">
                        ⚠️ Insufficient evidence in cluster to provide a 100% deterministic answer.
                      </div>
                    )}

                    {message.confidence !== undefined &&
                      message.confidence !== null && (
                        <div className="chat-confidence">
                          <span className="confidence-label">AI CONFIDENCE:</span>
                          <span className="confidence-val">
                            {(Number(message.confidence) * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}

                    {message.evidence.length > 0 && (
                      <div className="chat-section">
                        <h4>Empirical Evidence</h4>

                        {message.evidence.map(
                          (item, evidenceIndex) => (
                            <div
                              className="chat-evidence"
                              key={evidenceIndex}
                            >
                              {typeof item === "string"
                                ? item
                                : JSON.stringify(item)}
                            </div>
                          )
                        )}
                      </div>
                    )}

                    {message.citations.length > 0 && (
                      <div className="chat-section">
                        <h4>Audit Citations</h4>

                        {message.citations.map(
                          (citation, citationIndex) => (
                            <div
                              className="chat-citation"
                              key={citationIndex}
                            >
                              {typeof citation === "string"
                                ? citation
                                : JSON.stringify(citation)}
                            </div>
                          )
                        )}
                      </div>
                    )}

                    {message.recommendations.length > 0 && (
                      <div className="chat-section">
                        <h4>Remediation Recommendations</h4>

                        {message.recommendations.map(
                          (recommendation, recommendationIndex) => (
                            <div
                              className="chat-recommendation"
                              key={recommendationIndex}
                            >
                              {typeof recommendation === "string"
                                ? recommendation
                                : JSON.stringify(recommendation)}
                            </div>
                          )
                        )}
                      </div>
                    )}
                  </div>
                )}
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <div className="chat-message-label">
                <span className="sender-avatar">⚡</span> CognitiveOps Neural Agent
              </div>

              <div className="chat-message-content thinking-bubble">
                <span className="pulse-dot"></span>
                <span>{THINKING_PHRASES[thinkingIndex]}</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Pills Bar above Input */}
        {messages.length > 0 && (
          <div className="chat-quick-bar">
            {SUGGESTED_QUERIES.slice(0, 3).map((item, idx) => (
              <button
                key={idx}
                type="button"
                className="quick-chip"
                onClick={() => handleQuickPrompt(item.label)}
              >
                <span>{item.icon}</span> {item.label}
              </button>
            ))}
          </div>
        )}

        {/* Input Form Deck */}
        <form
          className="chat-input-area"
          onSubmit={handleSubmit}
        >
          <div className="chat-input-wrapper">
            <span className="input-prompt-icon">›_</span>
            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Query workflow intelligence, root cause DAGs, or SLA risk vectors..."
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? "PROCESSING..." : "DISPATCH"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default Chat;
