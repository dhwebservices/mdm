#!/usr/bin/env sh
set -eu

required_vars="
DATABASE_URL
REDIS_URL
JWT_ISSUER
JWT_AUDIENCE
JWT_JWKS_URL
PUBLIC_BASE_URL
CORS_ORIGINS
MDM_ORGANIZATION
MDM_TOPIC
MDM_SERVER_URL
MDM_CHECKIN_URL
MDM_SCEP_URL
MDM_SCEP_CHALLENGE
FILEVAULT_KEK
CLOUDFLARE_TUNNEL_TOKEN
"

missing=0
for name in $required_vars; do
  value=$(printenv "$name" 2>/dev/null || true)
  if [ -z "$value" ]; then
    echo "missing: $name"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "runtime environment is incomplete"
  exit 1
fi

case "$PUBLIC_BASE_URL" in
  https://*) ;;
  *)
    echo "PUBLIC_BASE_URL must use https for Apple MDM"
    exit 1
    ;;
esac

case "$MDM_TOPIC" in
  com.apple.mgmt.External.*) ;;
  *)
    echo "MDM_TOPIC must be the Apple MDM push topic"
    exit 1
    ;;
esac

echo "runtime environment looks complete"
