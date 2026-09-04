const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


export async function submitApproval(
  issueKey,
  decision
) {

  const response = await fetch(
    `${API_URL}/api/workflow/approval`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({

        issue_key:
          issueKey,

        decision:
          decision
      })
    }
  );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Approval request failed."
    );
  }


  return data;
}