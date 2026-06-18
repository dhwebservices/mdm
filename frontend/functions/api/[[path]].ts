export async function onRequest(context: {
  request: Request;
  env: { API_ORIGIN?: string };
  params: { path?: string | string[] };
}): Promise<Response> {
  const apiOrigin = context.env.API_ORIGIN;
  if (!apiOrigin) {
    return new Response("API_ORIGIN is not configured", { status: 500 });
  }

  const requestUrl = new URL(context.request.url);
  const targetUrl = new URL(requestUrl.pathname + requestUrl.search, apiOrigin);

  const headers = new Headers(context.request.headers);
  headers.set("X-Forwarded-Host", requestUrl.host);
  headers.set("X-Forwarded-Proto", requestUrl.protocol.replace(":", ""));

  return fetch(targetUrl, {
    method: context.request.method,
    headers,
    body: context.request.body,
    redirect: "manual",
  });
}
