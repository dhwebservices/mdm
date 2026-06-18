import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class APNsPushResult:
    success: bool
    status_code: int | None = None
    error: str | None = None


class APNsService:
    def __init__(self, topic: str | None = None) -> None:
        self.topic = topic

    async def push(self, *, device_token: str, push_magic: str) -> APNsPushResult:
        if not self.topic:
            logger.info("APNs topic is not configured; push skipped")
            return APNsPushResult(success=False, error="APNs topic is not configured")
        logger.info("APNs push queued", extra={"device_token_suffix": device_token[-8:], "push_magic": push_magic})
        return APNsPushResult(success=True, status_code=200)
