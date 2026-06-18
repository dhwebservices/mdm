from fastapi import APIRouter, Response

from app.services.certificates import CertificateService

router = APIRouter()


@router.get("/abm/public-key-certificate")
def download_abm_public_key_certificate() -> Response:
    certificate = CertificateService().ensure_abm_public_certificate()
    return Response(
        content=certificate,
        media_type="application/x-pem-file",
        headers={"Content-Disposition": 'attachment; filename="dh-mdm-abm-public-key.pem"'},
    )
