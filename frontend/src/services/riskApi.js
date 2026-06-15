const API_URL = import.meta.env.VITE_API_URL;

export async function getRiskScores() {
  const response = await fetch(
    `${API_URL}/api/risk`
  );

  return response.json();
}