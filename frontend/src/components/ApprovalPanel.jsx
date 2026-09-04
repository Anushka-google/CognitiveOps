import {
  useState
} from "react";

import {
  submitApproval
} from "../services/approvalApi";


function ApprovalPanel({
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


  if (
    !proposedAction ||
    !proposedAction.target
  ) {

    return null;

  }


  async function handleDecision(
    decision
  ) {

    console.log(
      "HITL DECISION:",
      {
        issueKey:
          proposedAction.target,

        decision:
          decision
      }
    );


    setLoading(true);

    setMessage("");

    setError("");


    try {

      const result =
        await submitApproval(
          proposedAction.target,
          decision
        );


      console.log(
        "HITL RESPONSE:",
        result
      );


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


      if (onComplete) {

        onComplete(
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

      setLoading(false);

    }

  }


  if (completed) {

    return (

      <section
        className="dashboard-section"
        id="human-approval"
      >

        <div
          style={{
            border:
              "1px solid rgba(80, 200, 120, 0.45)",

            borderRadius:
              "14px",

            padding:
              "24px",

            marginBottom:
              "24px",

            background:
              "rgba(80, 200, 120, 0.06)"
          }}
        >

          <span
            className="section-kicker"
          >
            HUMAN-IN-THE-LOOP
          </span>


          <h2>
            {
              decisionMade === "approve"
                ? "Action Approved"
                : "Action Rejected"
            }
          </h2>


          <p
            className="section-description"
          >
            {message}
          </p>


          <p
            style={{
              marginTop:
                "12px"
            }}
          >

            <strong>
              Ticket:
            </strong>{" "}

            {proposedAction.target}

          </p>


          <p>

            <strong>
              Decision:
            </strong>{" "}

            {decisionMade}

          </p>

        </div>

      </section>

    );

  }


  return (

    <section
      className="dashboard-section"
      id="human-approval"
    >

      <div
        style={{
          border:
            "1px solid rgba(255, 180, 0, 0.45)",

          borderRadius:
            "14px",

          padding:
            "24px",

          marginBottom:
            "24px",

          background:
            "rgba(255, 180, 0, 0.06)"
        }}
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


          <p
            className="section-description"
          >
            CognitiveOps detected a
            high-impact operational action.
            Human approval is required before
            Jira is modified.
          </p>

        </div>


        <div
          style={{
            marginTop:
              "18px",

            padding:
              "18px",

            borderRadius:
              "10px",

            background:
              "rgba(0, 0, 0, 0.15)"
          }}
        >

          <p>

            <strong>
              Ticket:
            </strong>{" "}

            {proposedAction.target}

          </p>


          <p>

            <strong>
              Action:
            </strong>{" "}

            {proposedAction.action_type}

          </p>


          <p>

            <strong>
              Field:
            </strong>{" "}

            {proposedAction.field}

          </p>


          <p>

            <strong>
              New Value:
            </strong>{" "}

            {proposedAction.new_value}

          </p>


          <p>

            <strong>
              Impact:
            </strong>{" "}

            {proposedAction.impact_level}

          </p>


          <p>

            <strong>
              Reason:
            </strong>{" "}

            {approvalReason ||
              proposedAction.description}

          </p>

        </div>


        <div
          style={{
            display:
              "flex",

            gap:
              "12px",

            marginTop:
              "20px"
          }}
        >

          <button
            type="button"
            disabled={loading}
            onClick={() =>
              handleDecision(
                "approve"
              )
            }
            style={{
              padding:
                "10px 20px",

              borderRadius:
                "8px",

              border:
                "none",

              cursor:
                loading
                  ? "not-allowed"
                  : "pointer",

              fontWeight:
                "600"
            }}
          >

            {
              loading
                ? "Processing..."
                : "Approve Action"
            }

          </button>


          <button
            type="button"
            disabled={loading}
            onClick={() =>
              handleDecision(
                "reject"
              )
            }
            style={{
              padding:
                "10px 20px",

              borderRadius:
                "8px",

              cursor:
                loading
                  ? "not-allowed"
                  : "pointer",

              fontWeight:
                "600"
            }}
          >

            Reject

          </button>

        </div>


        {error && (

          <p
            style={{
              marginTop:
                "16px"
            }}
          >

            {error}

          </p>

        )}

      </div>

    </section>

  );

}


export default ApprovalPanel;