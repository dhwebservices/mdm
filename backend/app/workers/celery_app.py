from celery import Celery

from app.core.config import settings

celery_app = Celery("dh_mdm", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="commands.dispatch")
def dispatch_command(command_id: str) -> dict[str, str]:
    return {"command_id": command_id, "status": "queued"}
