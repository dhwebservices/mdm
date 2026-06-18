from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import MDMMessage
from app.services.mdm import MDMService

router = APIRouter()


@router.post("/checkin")
def checkin(message: MDMMessage, db: Session = Depends(get_db)) -> dict[str, str]:
    payload = message.model_dump(by_alias=True, exclude_none=True)
    service = MDMService(db)
    message_type = payload.get("MessageType")
    if message_type == "TokenUpdate":
        service.token_update(payload)
    elif message_type == "CheckOut" and payload.get("UDID"):
        service.checkout(payload["UDID"])
    db.commit()
    return {"status": "ok"}


@router.post("/connect")
def connect(message: MDMMessage, db: Session = Depends(get_db)) -> dict:
    payload = message.model_dump(by_alias=True, exclude_none=True)
    service = MDMService(db)
    if payload.get("Status"):
        service.record_response(payload)
    response = service.next_command_payload(payload["UDID"]) if payload.get("UDID") else {"Status": "Idle"}
    db.commit()
    return response
