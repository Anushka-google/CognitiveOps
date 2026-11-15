import React, { useState, useEffect } from "react";
import { askChat } from "../services/chatApi";
import "./Chat.css";

const THINKING_PHRASES = [
  "🧠 Ingesting query into Hybrid RAG engine...",
  "🕸️ Checking DAG dependency graph for circular blockers...",
  "📊 Correlating Jira ticket SLA breach vectors...",
  "⚡ Synthesizing grounded operational intelligence...",
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
    event.preventDefault();

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

  return (
    <main className="chat-page">
      <div className="chat-header">
        <div>
          <h1>CognitiveOps Chat</h1>
          <p>
            Ask questions about workflows, risks,
            bottlenecks, Jira and operational evidence.
          </p>
        </div>
      </div>

      <section className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <h2>Ask CognitiveOps</h2>

              <p>
                Try asking:
              </p>

              <div className="chat-examples">
                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "Why is the workflow delayed?"
                    )
                  }
                >
                  Why is the workflow delayed?
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "Find the biggest bottleneck."
                    )
                  }
                >
                  Find the biggest bottleneck.
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setQuestion(
                      "What action should we take?"
                    )
                  }
                >
                  What action should we take?
                </button>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`chat-message ${message.role}`}
            >
              <div className="chat-message-label">
                {message.role === "user"
                  ? "You"
                  : "CognitiveOps"}
                {message.offlineFallback && (
                  <span style={{
                    marginLeft: "8px",
                    fontSize: "0.72rem",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    background: "rgba(56, 189, 248, 0.15)",
                    color: "#38bdf8",
                    border: "1px solid rgba(56, 189, 248, 0.3)"
                  }}>
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
                  <>
                    {message.insufficientEvidence && (
                      <div className="chat-warning">
                        There is not enough evidence to
                        provide a reliable answer.
                      </div>
                    )}

                    {message.confidence !== undefined &&
                      message.confidence !== null && (
                        <div className="chat-confidence">
                          Confidence:{" "}
                          {Number(
                            message.confidence
                          ).toFixed(2)}
                        </div>
                      )}

                    {message.evidence.length > 0 && (
                      <div className="chat-section">
                        <h3>Evidence</h3>

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
                        <h3>Citations</h3>

                        {message.citations.map(
                          (citation, citationIndex) => (
                            <div
                              className="chat-citation"
                              key={citationIndex}
                            >
                              {typeof citation === "string"
                                ? citation
                                : JSON.stringify(
                                    citation
                                  )}
                            </div>
                          )
                        )}
                      </div>
                    )}

                    {message.recommendations.length >
                      0 && (
                      <div className="chat-section">
                        <h3>Recommendations</h3>

                        {message.recommendations.map(
                          (
                            recommendation,
                            recommendationIndex
                          ) => (
                            <div
                              className="chat-recommendation"
                              key={recommendationIndex}
                            >
                              {typeof recommendation ===
                              "string"
                                ? recommendation
                                : JSON.stringify(
                                    recommendation
                                  )}
                            </div>
                          )
                        )}
                      </div>
                    )}
                  </>
                )}
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <div className="chat-message-label">
                CognitiveOps
              </div>

              <div className="chat-message-content" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="pulse-dot" style={{ width: "8px", height: "8px" }}></span>
                <span>{THINKING_PHRASES[thinkingIndex]}</span>
              </div>
            </div>
          )}
        </div>

        <form
          className="chat-input-area"
          onSubmit={handleSubmit}
        >
          <input
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask a workflow question..."
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? "..." : "Send"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default Chat;
