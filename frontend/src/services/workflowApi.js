const API_URL = import.meta.env.VITE_API_URL;

export async function getWorkflowAnalysis() {
  const response = await fetch(
    `${API_URL}/api/workflow/analyze`,
    {
      method: "POST",
    }
  );

  const data = await response.json();

  return data;
}

export async function getRootCauseGraph() {
  const response = await fetch(
    `${API_URL}/api/workflow/root-cause-graph`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load root cause graph.");
  }

  return data;
}

export async function getExecutiveSummary() {
  const response = await fetch(
    `${API_URL}/api/workflow/executive-summary`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load executive summary.");
  }

  return data;
}

export async function getTrendForecast() {
  const response = await fetch(
    `${API_URL}/api/workflow/trend-forecast`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load trend forecast.");
  }

  return data;
}