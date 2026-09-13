const API_URL = import.meta.env.VITE_API_URL;

export async function getJiraStatus() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/jira/env-check`, {
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  if (!response.ok) throw new Error("Failed to fetch Jira status");
  return await response.json();
}

export async function testJiraConnection() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/jira/test`, {
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  if (!response.ok) throw new Error("Failed to test Jira connection");
  return await response.json();
}

export async function getSlackStatus() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/slack/status`, {
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  if (!response.ok) throw new Error("Failed to fetch Slack status");
  return await response.json();
}

export async function testSlackConnection() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/slack/test`, {
    method: "POST",
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  if (!response.ok) throw new Error("Failed to test Slack connection");
  return await response.json();
}
