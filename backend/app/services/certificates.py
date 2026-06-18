from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.core.config import settings


class CertificateService:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path("/app/data/certificates")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def abm_private_key_path(self) -> Path:
        return self.data_dir / "abm_server_token_private_key.pem"

    @property
    def abm_public_cert_path(self) -> Path:
        return self.data_dir / "abm_server_token_public_cert.pem"

    def ensure_abm_public_certificate(self) -> bytes:
        if self.abm_public_cert_path.exists() and self.abm_private_key_path.exists():
            return self.abm_public_cert_path.read_bytes()

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, settings.mdm_organization),
                x509.NameAttribute(NameOID.COMMON_NAME, "DH MDM ABM Server Token Encryption"),
            ]
        )
        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=False, key_encipherment=True, content_commitment=False, data_encipherment=True, key_agreement=False, key_cert_sign=False, crl_sign=False, encipher_only=False, decipher_only=False), critical=True)
            .sign(private_key=private_key, algorithm=hashes.SHA256())
        )

        self.abm_private_key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        self.abm_private_key_path.chmod(0o600)

        cert_bytes = certificate.public_bytes(serialization.Encoding.PEM)
        self.abm_public_cert_path.write_bytes(cert_bytes)
        self.abm_public_cert_path.chmod(0o644)
        return cert_bytes

    @property
    def abm_server_token_path(self) -> Path:
        return self.data_dir / "abm_server_token.p7m"

    def store_abm_server_token(self, token_bytes: bytes) -> Path:
        if not token_bytes:
            raise ValueError("ABM server token is empty")
        self.abm_server_token_path.write_bytes(token_bytes)
        self.abm_server_token_path.chmod(0o600)
        return self.abm_server_token_path

    def abm_server_token_status(self) -> dict[str, object]:
        if not self.abm_server_token_path.exists():
            return {"uploaded": False, "size": 0}
        stat = self.abm_server_token_path.stat()
        return {"uploaded": True, "size": stat.st_size}

    @property
    def apns_private_key_path(self) -> Path:
        return self.data_dir / "apns_mdm_private_key.pem"

    @property
    def apns_csr_path(self) -> Path:
        return self.data_dir / "apns_mdm.csr"

    @property
    def apns_certificate_path(self) -> Path:
        return self.data_dir / "apns_mdm_certificate.pem"

    def ensure_apns_csr(self) -> bytes:
        if self.apns_csr_path.exists() and self.apns_private_key_path.exists():
            return self.apns_csr_path.read_bytes()

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(NameOID.ORGANIZATION_NAME, settings.mdm_organization),
                        x509.NameAttribute(NameOID.COMMON_NAME, "DH MDM APNs MDM Push Certificate"),
                    ]
                )
            )
            .sign(private_key, hashes.SHA256())
        )

        self.apns_private_key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        self.apns_private_key_path.chmod(0o600)

        csr_bytes = csr.public_bytes(serialization.Encoding.PEM)
        self.apns_csr_path.write_bytes(csr_bytes)
        self.apns_csr_path.chmod(0o644)
        return csr_bytes

    def store_apns_certificate(self, certificate_bytes: bytes) -> dict[str, object]:
        if not certificate_bytes:
            raise ValueError("APNs certificate is empty")

        certificate = self._load_certificate(certificate_bytes)
        topic = self._extract_apns_topic(certificate)
        self.apns_certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        self.apns_certificate_path.chmod(0o600)
        return {"uploaded": True, "topic": topic, "expires_at": certificate.not_valid_after_utc.isoformat()}

    def apns_certificate_status(self) -> dict[str, object]:
        if not self.apns_certificate_path.exists():
            return {"uploaded": False, "topic": None, "expires_at": None}
        certificate = self._load_certificate(self.apns_certificate_path.read_bytes())
        return {
            "uploaded": True,
            "topic": self._extract_apns_topic(certificate),
            "expires_at": certificate.not_valid_after_utc.isoformat(),
        }

    def _load_certificate(self, certificate_bytes: bytes) -> x509.Certificate:
        try:
            return x509.load_pem_x509_certificate(certificate_bytes)
        except ValueError:
            return x509.load_der_x509_certificate(certificate_bytes)

    def _extract_apns_topic(self, certificate: x509.Certificate) -> str | None:
        for attribute in certificate.subject:
            value = str(attribute.value)
            if value.startswith("com.apple.mgmt."):
                return value
        for attribute in certificate.subject:
            value = str(attribute.value)
            if "com.apple.mgmt." in value:
                return value[value.index("com.apple.mgmt.") :]
        return None
