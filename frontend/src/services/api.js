export async function getRiskScores() {

  const response = await fetch(
    "http://127.0.0.1:8000/api/risk"
  );

  return response.json();
}