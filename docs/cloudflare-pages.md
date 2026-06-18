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
VITE_API_BASE_URL=https://mdm.yourdomain.com/api/v1
```

Use the public FastAPI backend URL served by Cloudflare Tunnel or your production container host.

## Custom Domain Split

Recommended:

- Portal: `https://portal.yourdomain.com` on Cloudflare Pages
- MDM API: `https://mdm.yourdomain.com` through Cloudflare Tunnel to Nginx/backend

Apple device enrollment must use the API hostname, not the static Pages hostname.
