from fastapi import APIRouter

from app.api.v1 import audit, dashboard, devices, enrollment, mdm, notifications

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(audit.router, prefix="/audit-log", tags=["audit-log"])
api_router.include_router(mdm.router, prefix="/mdm", tags=["mdm"])
api_router.include_router(enrollment.router, prefix="/enrollment", tags=["enrollment"])
