export async function getWorkflowAnalysis() {
  const response = await fetch(
    "http://127.0.0.1:8000/api/workflow/analyze",
    {
      method: "POST",
    }
  );

  const data = await response.json();

  return data;
}