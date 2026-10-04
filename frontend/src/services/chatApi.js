import { API_URL } from "./apiConfig";

export async function askChat(question) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `${API_URL}/api/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": token ? `Bearer ${token}` : "",
      },
      body: JSON.stringify({ question }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Chat request failed."
    );
  }

  return data;
}