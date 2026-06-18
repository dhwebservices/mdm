from fastapi import APIRouter, HTTPException, Query, Response

from app.services.enrollment import EnrollmentProfileService

router = APIRouter()


@router.get("/mobileconfig")
def download_mobileconfig(platform: str = Query(default="macos", pattern="^(macos|ios)$")) -> Response:
    try:
        body = EnrollmentProfileService().mobileconfig(platform=platform)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="Unable to generate enrollment profile") from exc
    filename = f"dh-mdm-{platform}.mobileconfig"
    return Response(
        content=body,
        media_type="application/x-apple-aspen-config",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
