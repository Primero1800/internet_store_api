import logging
from typing import TYPE_CHECKING
import asyncio

from celery.exceptions import MaxRetriesExceededError

from celery_home.config import app_celery

if TYPE_CHECKING:
    from src.api.v1.email_sender.schemas import CustomMessageSchema


logger = logging.getLogger(__name__)


@app_celery.task(bind=True, name="task_send_mail")
def task_send_mail(
        self,
        schema: dict,
) -> dict:
    meta = {
        'app_name': '3_sur_app1',
        'task_name': self.name,
        'args': tuple(),
        'kwargs': schema,
    }
    self.update_state(meta={'task_name': self.name})
    from src.api.v1.email_sender.schemas import CustomMessageSchema
    schema = CustomMessageSchema(**schema)
    from src.scrypts.mail_sender.utils import send_mail
    result: bool = False

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            result = asyncio.run(send_mail(schema))
        else:
            result = loop.run_until_complete(send_mail(schema))
        if not result:
            raise self.retry(countdown=5, max_retries=3)
    except MaxRetriesExceededError as exc:
        logger.error(f'Task {self.name!r} error: {exc}')
    return {
        "meta": meta,
        "returned_value": result
    }