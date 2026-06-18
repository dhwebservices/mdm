# Cloudflare Deployment

DH MDM is Cloudflare-ready through an Nginx edge service and optional Cloudflare Tunnel.

## Public URL

Apple MDM requires stable public HTTPS URLs for check-in and command connection.

Set:

```bash
PUBLIC_BASE_URL=https://mdm.dhwebsiteservices.co.uk
MDM_SERVER_URL=https://mdm.dhwebsiteservices.co.uk/api/v1/mdm/connect
MDM_CHECKIN_URL=https://mdm.dhwebsiteservices.co.uk/api/v1/mdm/checkin
CORS_ORIGINS=https://mdm.dhwebsiteservices.co.uk
```

## Tunnel

Create a Cloudflare Tunnel for the backend origin and point it at the local Nginx service:

```text
http://nginx:8080
```

If `mdm.dhwebsiteservices.co.uk` is attached to Cloudflare Pages, do not attach the same hostname directly to the Tunnel. Instead, expose the backend at another protected origin and set Cloudflare Pages `API_ORIGIN` to that URL. The Pages Function will proxy `https://mdm.dhwebsiteservices.co.uk/api/*` to the backend.

Then set:

```bash
CLOUDFLARE_TUNNEL_TOKEN=...
```

Run:

```bash
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml --profile tunnel up --build
```

If Cloudflare Pages is hosting the React portal, run only the API stack locally:

```bash
docker compose -f docker-compose.api.yml up --build
```

Then point the Tunnel route at:

```text
http://localhost:8080
```

## R2

R2 is reserved for large artifacts such as PKG uploads and script output. Set the R2 variables in `.env` before enabling those storage-backed services.
