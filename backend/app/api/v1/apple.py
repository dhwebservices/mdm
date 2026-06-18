from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

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


@router.get("/abm/server-token/status")
def abm_server_token_status() -> dict[str, object]:
    return CertificateService().abm_server_token_status()


@router.post("/abm/server-token", status_code=status.HTTP_201_CREATED)
async def upload_abm_server_token(file: UploadFile = File(...)) -> dict[str, object]:
    filename = file.filename or ""
    if not filename.endswith(".p7m"):
        raise HTTPException(status_code=400, detail="Upload the Apple Business Manager .p7m server token")
    content = await file.read()
    path = CertificateService().store_abm_server_token(content)
    return {"uploaded": True, "filename": filename, "size": path.stat().st_size}


@router.get("/apns/csr")
def download_apns_csr() -> Response:
    csr = CertificateService().ensure_apns_csr()
    return Response(
        content=csr,
        media_type="application/x-pem-file",
        headers={"Content-Disposition": 'attachment; filename="dh-mdm-apns-mdm.csr"'},
    )


@router.get("/apns/certificate/status")
def apns_certificate_status() -> dict[str, object]:
    return CertificateService().apns_certificate_status()


@router.post("/apns/certificate", status_code=status.HTTP_201_CREATED)
async def upload_apns_certificate(file: UploadFile = File(...)) -> dict[str, object]:
    filename = file.filename or ""
    if not filename.endswith((".pem", ".cer", ".crt")):
        raise HTTPException(status_code=400, detail="Upload the Apple-issued APNs MDM certificate")
    content = await file.read()
    try:
        result = CertificateService().store_apns_certificate(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid APNs certificate") from exc
    return {"filename": filename, **result}
