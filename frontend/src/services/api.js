import { API_URL } from "./apiConfig";

export async function getWorkflowAnalysis() {
  const response = await fetch(
    `${API_URL}/api/workflow/analyze`,
    {
      method: "POST",
    }
  );

  return response.json();
}