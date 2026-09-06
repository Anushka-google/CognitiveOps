import { useState } from "react";

import {
  submitApproval
} from "../services/approvalApi";


// =====================================================
// Approval Panel
// =====================================================

function ApprovalPanel({
  executionId,
  proposedAction,
  approvalReason,
  onComplete
}) {

  const [
    loading,
    setLoading
  ] = useState(false);


  const [
    completed,
    setCompleted
  ] = useState(false);


  const [
    decisionMade,
    setDecisionMade
  ] = useState("");


  const [
    message,
    setMessage
  ] = useState("");


  const [
    error,
    setError
  ] = useState("");


  // =====================================================
  // Safety Check
  // =====================================================

  if (
    !executionId ||
    !proposedAction ||
    !proposedAction.target
  ) {

    return null;

  }


  // =====================================================
  // Handle Approval Decision
  // =====================================================

  async function handleDecision(
    decision
  ) {

    console.log(
      "HITL DECISION:",
      {
        executionId,
        decision,
        proposedAction
      }
    );


    setLoading(true);

    setMessage("");

    setError("");


    try {

      // =========================================
      // Send decision to backend
      // =========================================

      const result =
        await submitApproval(
          executionId,
          decision
        );


      console.log(
        "HITL RESPONSE:",
        result
      );


      // =========================================
      // Update UI
      // =========================================

      setDecisionMade(
        decision
      );

      setCompleted(
        true
      );


      setMessage(

        result.message ||

        (
          decision === "approve"

            ? "Action approved successfully."

            : "Action rejected successfully."

        )

      );


      // =========================================
      // Refresh parent dashboard
      // =========================================

      if (onComplete) {

        await onComplete(
          result
        );

      }

    }

    catch (err) {

      console.error(
        "Approval error:",
        err
      );


      setError(
        err.message ||
        "Approval failed."
      );

    }

    finally {

      setLoading(
        false
      );

    }

  }


  // =====================================================
  // Completed State
  // =====================================================

  if (completed) {

    const approved =
      decisionMade === "approve";


    return (

      <section
        className="dashboard-section"
      >

        <div
          className="table-panel"
          style={{
            padding: "24px",
            marginBottom: "24px"
          }}
        >

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "20px",
              flexWrap: "wrap"
            }}
          >

            <div>

              <span
                className="section-kicker"
              >
                HUMAN-IN-THE-LOOP
              </span>


              <h2
                style={{
                  marginBottom: "8px"
                }}
              >

                {
                  approved
                    ? "Action Approved"
                    : "Action Rejected"
                }

              </h2>


              <p>

                {
                  message
                }

              </p>

            </div>


            <div
              style={{
                fontWeight: "600",
                fontSize: "14px"
              }}
            >

              Execution #

              {
                executionId
              }

            </div>

          </div>


          <div
            style={{
              marginTop: "20px",
              padding: "16px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.04)"
            }}
          >

            <strong>
              Action
            </strong>


            <p
              style={{
                marginTop: "8px"
              }}
            >

              {
                proposedAction.target
              }

              {" → "}

              {
                proposedAction.new_value ||
                proposedAction.newValue ||
                "N/A"
              }

            </p>

          </div>

        </div>

      </section>

    );

  }


  // =====================================================
  // Approval Required State
  // =====================================================

  return (

    <section
      className="dashboard-section"
    >

      <div
        className="table-panel"
        style={{
          padding: "24px",
          marginBottom: "24px"
        }}
      >

        {/* =========================================
            HEADER
        ========================================= */}

        <div
          className="section-label-row"
        >

          <div>

            <span
              className="section-kicker"
            >
              HUMAN-IN-THE-LOOP
            </span>


            <h2>
              Approval Required
            </h2>

          </div>


          <span
            className="ai-generated"
          >
            Pending
          </span>

        </div>


        {/* =========================================
            EXECUTION INFORMATION
        ========================================= */}

        <div
          style={{
            marginTop: "20px"
          }}
        >

          <p>

            CognitiveOps has proposed an action
            that requires human approval before
            execution.

          </p>


          <div
            style={{
              marginTop: "16px",
              padding: "16px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.04)"
            }}
          >

            <div
              style={{
                marginBottom: "10px"
              }}
            >

              <strong>
                Execution ID:
              </strong>

              {" "}

              #
              {
                executionId
              }

            </div>


            <div
              style={{
                marginBottom: "10px"
              }}
            >

              <strong>
                Proposed Action:
              </strong>

              {" "}

              {
                proposedAction.target
              }

              {" → "}

              {
                proposedAction.new_value ||
                proposedAction.newValue ||
                "N/A"
              }

            </div>


            {
              proposedAction.type && (

                <div>

                  <strong>
                    Action Type:
                  </strong>

                  {" "}

                  {
                    proposedAction.type
                  }

                </div>

              )
            }

          </div>

        </div>


        {/* =========================================
            APPROVAL REASON
        ========================================= */}

        {
          approvalReason && (

            <div
              style={{
                marginTop: "16px",
                padding: "16px",
                borderRadius: "10px",
                background: "rgba(255,255,255,0.04)"
              }}
            >

              <strong>
                Approval Reason
              </strong>


              <p
                style={{
                  marginTop: "8px"
                }}
              >

                {
                  approvalReason
                }

              </p>

            </div>

          )
        }


        {/* =========================================
            ERROR
        ========================================= */}

        {
          error && (

            <div
              style={{
                marginTop: "16px",
                padding: "12px 16px",
                borderRadius: "8px",
                border: "1px solid rgba(255,80,80,0.4)",
                background: "rgba(255,80,80,0.08)"
              }}
            >

              <strong>
                Approval Error
              </strong>


              <p
                style={{
                  marginTop: "6px"
                }}
              >

                {
                  error
                }

              </p>

            </div>

          )
        }


        {/* =========================================
            ACTION BUTTONS
        ========================================= */}

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginTop: "24px",
            flexWrap: "wrap"
          }}
        >

          {/* =====================================
              REJECT
          ===================================== */}

          <button

            type="button"

            disabled={
              loading
            }

            onClick={() =>
              handleDecision(
                "reject"
              )
            }

            style={{
              padding: "12px 22px",
              borderRadius: "8px",
              border: "1px solid rgba(255,255,255,0.15)",
              cursor: loading
                ? "not-allowed"
                : "pointer",
              opacity: loading
                ? 0.6
                : 1
            }}

          >

            {
              loading
                ? "Processing..."
                : "Reject"
            }

          </button>


          {/* =====================================
              APPROVE
          ===================================== */}

          <button

            type="button"

            disabled={
              loading
            }

            onClick={() =>
              handleDecision(
                "approve"
              )
            }

            style={{
              padding: "12px 22px",
              borderRadius: "8px",
              border: "none",
              cursor: loading
                ? "not-allowed"
                : "pointer",
              opacity: loading
                ? 0.6
                : 1
            }}

          >

            {
              loading
                ? "Processing..."
                : "Approve"
            }

          </button>

        </div>

      </div>

    </section>

  );

}


export default ApprovalPanel;