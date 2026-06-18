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
