import plistlib
import uuid
from datetime import datetime, timezone

from app.core.config import settings


class EnrollmentProfileService:
    def mobileconfig(self, *, platform: str) -> bytes:
        profile_uuid = str(uuid.uuid4()).upper()
        mdm_payload_uuid = str(uuid.uuid4()).upper()
        scep_payload_uuid = str(uuid.uuid4()).upper()
        now = datetime.now(timezone.utc).replace(microsecond=0)

        scep_payload = {
            "PayloadType": "com.apple.security.scep",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.dhwebservices.mdm.scep.{platform}",
            "PayloadUUID": scep_payload_uuid,
            "PayloadDisplayName": "DH MDM Device Identity",
            "URL": settings.mdm_scep_url,
            "Name": "DH MDM Device Identity",
            "Subject": [[["O", settings.mdm_organization]], [["CN", "DH MDM Device"]]],
            "Challenge": settings.mdm_scep_challenge,
            "Keysize": 2048,
            "Key Type": "RSA",
            "Key Usage": 5,
        }

        mdm_payload = {
            "PayloadType": "com.apple.mdm",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.dhwebservices.mdm.payload.{platform}",
            "PayloadUUID": mdm_payload_uuid,
            "PayloadDisplayName": "DH MDM",
            "AccessRights": 8191,
            "CheckInURL": settings.mdm_checkin_url,
            "ServerURL": settings.mdm_server_url,
            "Topic": settings.mdm_topic,
            "IdentityCertificateUUID": scep_payload_uuid,
            "SignMessage": True,
            "CheckOutWhenRemoved": True,
            "ServerCapabilities": ["com.apple.mdm.per-user-connections"],
        }

        profile = {
            "PayloadType": "Configuration",
            "PayloadVersion": 1,
            "PayloadIdentifier": f"com.dhwebservices.mdm.enrollment.{platform}",
            "PayloadUUID": profile_uuid,
            "PayloadDisplayName": "DH MDM Enrollment",
            "PayloadDescription": "Enroll this device with DH Website Services MDM.",
            "PayloadOrganization": settings.mdm_organization,
            "PayloadRemovalDisallowed": False,
            "PayloadScope": "System",
            "PayloadContent": [scep_payload, mdm_payload],
            "PayloadExpirationDate": now.replace(year=now.year + 1),
        }
        return plistlib.dumps(profile, fmt=plistlib.FMT_XML, sort_keys=False)
