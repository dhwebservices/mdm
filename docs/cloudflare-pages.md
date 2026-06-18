# Cloudflare Pages

Use Cloudflare Pages for the React portal only. The FastAPI MDM backend cannot run on Pages; it needs the Docker/Nginx/Cloudflare Tunnel path documented in `docs/cloudflare.md`.

## Pages Build Settings

For the `dhwebservices/mdm` GitHub repository:

| Setting | Value |
|---|---|
| Framework preset | `None` or `React (Vite)` |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Root directory | `frontend` |

Do not use `/` as the output directory for this repo. The portal is a Vite app inside the `frontend` monorepo folder, and Cloudflare Pages should upload `frontend/dist`.

Cloudflare's Pages documentation lists React/Vite as `npm run build` with output directory `dist`.

## Environment Variables

Set this in Cloudflare Pages:

```bash
VITE_API_BASE_URL=/api/v1
API_ORIGIN=https://YOUR_BACKEND_TUNNEL_ORIGIN
```

`API_ORIGIN` is used by the Pages Function in `frontend/functions/api/[[path]].ts` to proxy `/api/*` to FastAPI. Point it at the backend origin served by Cloudflare Tunnel or your production container host.

## Custom Domain Split

Configured public hostname:

- Portal: `https://mdm.dhwebsiteservices.co.uk` on Cloudflare Pages
- MDM API: `https://mdm.dhwebsiteservices.co.uk/api/*` proxied by a Cloudflare Pages Function to `API_ORIGIN`

Apple device enrollment must use the API hostname, not the static Pages hostname.
