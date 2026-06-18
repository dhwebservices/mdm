# Runtime Configuration

Secrets must stay out of Git. Use `.env` locally or your production secret manager.

The local `.env` file is ignored by Git. To validate a runtime environment without printing secret values:

```bash
set -a
. ./.env
set +a
./scripts/check-runtime-env.sh
```

For Cloudflare Tunnel, set:

```bash
CLOUDFLARE_TUNNEL_TOKEN=...
```

For the current production hostname:

```bash
PUBLIC_BASE_URL=https://mdm.dhwebsiteservices.co.uk
CORS_ORIGINS=https://mdm.dhwebsiteservices.co.uk
MDM_SERVER_URL=https://mdm.dhwebsiteservices.co.uk/api/v1/mdm/connect
MDM_CHECKIN_URL=https://mdm.dhwebsiteservices.co.uk/api/v1/mdm/checkin
MDM_SCEP_URL=https://mdm.dhwebsiteservices.co.uk/scep
```

Apple enrollment will still fail until the APNs MDM topic/certificate and SCEP/device identity service are real production values.
