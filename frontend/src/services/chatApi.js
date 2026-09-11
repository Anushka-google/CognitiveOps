const API_URL = import.meta.env.VITE_API_URL;

export async function askChat(question) {
  const response = await fetch(
    `${API_URL}/api/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
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