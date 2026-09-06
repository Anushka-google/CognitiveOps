const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


// =====================================================
// Get Pending Human Approval
// =====================================================

export async function getPendingApproval() {

  const response =
    await fetch(
      `${API_URL}/api/executions/pending-approval`
    );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Failed to fetch pending approval"
    );

  }


  return data;
}


// =====================================================
// Submit Approval Decision
// =====================================================

export async function submitApproval(
  executionId,
  decision
) {

  const action =
    decision === "approve"
      ? "approve"
      : "reject";


  const response =
    await fetch(
      `${API_URL}/api/executions/${executionId}/${action}`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        }
      }
    );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Approval request failed."
    );

  }


  return data;
}


// =====================================================
// Approve Execution
// =====================================================

export async function approveExecution(
  executionId
) {

  return await submitApproval(
    executionId,
    "approve"
  );

}


// =====================================================
// Reject Execution
// =====================================================

export async function rejectExecution(
  executionId
) {

  return await submitApproval(
    executionId,
    "reject"
  );

}