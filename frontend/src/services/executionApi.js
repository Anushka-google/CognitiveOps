const API_URL =
  import.meta.env.VITE_API_URL;


// =====================================================
// Get Executions
// =====================================================

export async function getExecutions(
  offset = 0,
  limit = 20
) {

  const response =
    await fetch(
      `${API_URL}/api/executions/?offset=${offset}&limit=${limit}`
    );

  if (!response.ok) {

    throw new Error(
      "Failed to fetch executions"
    );
  }

  return await response.json();
}


// =====================================================
// Get Execution Statistics
// =====================================================

export async function getExecutionStats() {

  const response =
    await fetch(
      `${API_URL}/api/executions/stats/summary`
    );

  if (!response.ok) {

    throw new Error(
      "Failed to fetch execution statistics"
    );
  }

  return await response.json();
}


// =====================================================
// Get Pending Human Approval
// =====================================================

export async function getPendingApproval() {

  const response =
    await fetch(
      `${API_URL}/api/executions/pending-approval`
    );

  if (!response.ok) {

    throw new Error(
      "Failed to fetch pending approval"
    );
  }

  return await response.json();
}


// =====================================================
// Approve Execution
// =====================================================

export async function approveExecution(
  executionId
) {

  const response =
    await fetch(
      `${API_URL}/api/executions/${executionId}/approve`,
      {
        method: "POST"
      }
    );

  const data =
    await response.json();

  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Failed to approve execution"
    );
  }

  return data;
}


// =====================================================
// Reject Execution
// =====================================================

export async function rejectExecution(
  executionId
) {

  const response =
    await fetch(
      `${API_URL}/api/executions/${executionId}/reject`,
      {
        method: "POST"
      }
    );

  const data =
    await response.json();

  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Failed to reject execution"
    );
  }

  return data;
}