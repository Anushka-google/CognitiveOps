const API_URL = import.meta.env.VITE_API_URL;

export async function getWorkflowAnalysis() {
  const response = await fetch(
    `${API_URL}/api/workflow/analyze`,
    {
      method: "POST",
    }
  );

  return response.json();
}