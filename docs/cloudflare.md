# Cloudflare Deployment

DH MDM is Cloudflare-ready through an Nginx edge service and optional Cloudflare Tunnel.

## Public URL

Apple MDM requires stable public HTTPS URLs for check-in and command connection.

Set:

```bash
PUBLIC_BASE_URL=https://mdm.yourdomain.com
MDM_SERVER_URL=https://mdm.yourdomain.com/api/v1/mdm/connect
MDM_CHECKIN_URL=https://mdm.yourdomain.com/api/v1/mdm/checkin
CORS_ORIGINS=https://mdm.yourdomain.com
```

## Tunnel

Create a Cloudflare Tunnel for the hostname and point it at the local Nginx service:

```text
http://nginx:8080
```

Then set:

```bash
CLOUDFLARE_TUNNEL_TOKEN=...
```

Run:

```bash
docker compose -f docker-compose.yml -f docker-compose.cloudflare.yml --profile tunnel up --build
```

## R2

R2 is reserved for large artifacts such as PKG uploads and script output. Set the R2 variables in `.env` before enabling those storage-backed services.
