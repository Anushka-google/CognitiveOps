import { API_URL } from "./apiConfig";

export async function getRiskScores() {
  const response = await fetch(
    `${API_URL}/api/risk`
  );

  return response.json();
}