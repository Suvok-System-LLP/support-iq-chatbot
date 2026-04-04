export default async (request, context) => {
  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  const body = await request.json();

  const CLOUD_RUN_URL = "https://supportiq-chatbot-746238216503.australia-southeast1.run.app/chat";
  const SERVICE_ACCOUNT_TOKEN = Deno.env.get("GCP_ID_TOKEN");

  const response = await fetch(CLOUD_RUN_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${SERVICE_ACCOUNT_TOKEN}`,
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
};

export const config = { path: "/api/chat" };
