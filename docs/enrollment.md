# Enrollment Package

The backend exposes an Apple configuration profile download endpoint:

```text
GET /api/v1/enrollment/mobileconfig?platform=macos
GET /api/v1/enrollment/mobileconfig?platform=ios
```

The response is a `.mobileconfig` profile containing:

- MDM payload
- check-in URL
- server URL
- APNs topic
- SCEP identity payload reference
- supervised / server capability metadata

This profile is generated from environment variables. It must be configured with a real APNs MDM topic and SCEP/device identity service before it can enroll real devices.

For production, the generated profile should be signed with a trusted certificate before distribution.
