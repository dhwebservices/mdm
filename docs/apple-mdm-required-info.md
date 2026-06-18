# Apple MDM Required Information

To make DH MDM enroll real Macs, iPhones, and iPads, provide the following production values.

## Public Service

- Public HTTPS hostname, for example `https://mdm.dhwebsiteservices.com`
- Cloudflare Tunnel token or DNS target
- TLS must terminate publicly with a trusted certificate

## Apple Push Notification Service for MDM

- Apple MDM Push Certificate topic, usually `com.apple.mgmt.External.<uuid>`
- APNs MDM certificate/private key or APNs token-auth credentials appropriate for the MDM push certificate
- Apple ID used to renew the MDM push certificate
- Certificate expiry date

## Apple Business Manager

- ABM server token `.p7m`
- ADE default enrollment profile choices:
  - mandatory MDM
  - non-removable MDM
  - await device configured
  - Setup Assistant skip list
- Supervision and organization display name

## SCEP or Device Identity

Apple MDM enrollment needs a device identity. Provide one of:

- SCEP URL and challenge, or
- an internal CA flow for issuing device identity certificates

The current `.mobileconfig` generator expects SCEP values:

```bash
MDM_SCEP_URL=https://mdm.dhwebsiteservices.co.uk/scep
MDM_SCEP_CHALLENGE=...
```

## Microsoft Entra

- Entra tenant ID
- API app registration client ID / App ID URI
- Portal app registration client ID
- Redirect URI for the portal
- Role/group mapping for Admin, IT Manager, Helpdesk, Read Only

## FileVault

- 32-byte or stronger `FILEVAULT_KEK`
- Decision on future KEK backend: Hashicorp Vault, Azure Key Vault, AWS KMS, or other HSM-backed storage

## Cloudflare R2

- Account ID
- Bucket name
- Access key ID
- Secret access key
