# DH MDM

Internal Apple MDM platform for DH Website Services.

## Stack

- Backend: FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, Celery
- Frontend: React, TypeScript, Tailwind, React Query
- Auth: Microsoft Entra ID OAuth/JWT
- Apple: ABM/ADE, APNs, native MDM protocol foundations

## Local development

```bash
docker compose up --build
```

Backend API: `http://localhost:8000`

Frontend portal: `http://localhost:5173`

Enrollment profile download:

- `http://localhost:8000/api/v1/enrollment/mobileconfig?platform=macos`
- `http://localhost:8000/api/v1/enrollment/mobileconfig?platform=ios`

ABM public key certificate download:

- `http://localhost:8000/api/v1/apple/abm/public-key-certificate`

Cloudflare Tunnel deployment is documented in [docs/cloudflare.md](docs/cloudflare.md).

Cloudflare Pages settings for the React portal are documented in [docs/cloudflare-pages.md](docs/cloudflare-pages.md).

Apple MDM production inputs are listed in [docs/apple-mdm-required-info.md](docs/apple-mdm-required-info.md).

Runtime secret handling is documented in [docs/runtime.md](docs/runtime.md).

## Notes

The approved PostgreSQL schema was not present in the workspace. The initial migration preserves the requested table names and production-oriented relationships so development can continue; replace or reconcile it with the approved DDL when that file is available.
