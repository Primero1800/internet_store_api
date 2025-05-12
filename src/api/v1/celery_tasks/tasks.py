import logging
from typing import TYPE_CHECKING
import asyncio

from celery.exceptions import MaxRetriesExceededError

from celery_home.config import app_celery


logger = logging.getLogger(__name__)


@app_celery.task(bind=True, name="task_send_mail")
def task_send_mail(
        self,
        schema: dict,
) -> dict:
    meta = {
        'app_name': '4_sur_src',
        'task_name': self.name,
        'args': tuple(),
        'kwargs': schema,
    }
    self.update_state(meta={'task_name': self.name})
    from src.api.v1.message_senders import CustomMessageSchema
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


@app_celery.task(bind=True, name="task_send_tg_message")
def task_send_tg_message(
        self,
        schema: dict,
) -> dict:
    meta = {
        'app_name': '4_sur_src',
        'task_name': self.name,
        'args': tuple(),
        'kwargs': schema,
    }
    self.update_state(meta={'task_name': self.name})
    from src.api.v1.message_senders import CustomTgMessageSchema

    schema = CustomTgMessageSchema(**schema)
    from src.scrypts.telegram_message_sender.utils import send_tg_bot_message
    result: bool = False

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            result = asyncio.run(send_tg_bot_message(schema))
        else:
            result = loop.run_until_complete(send_tg_bot_message(schema))
        if not result:
            raise self.retry(countdown=5, max_retries=3)
    except MaxRetriesExceededError as exc:
        logger.error(f'Task {self.name!r} error: {exc}')
    return {
        "meta": meta,
        "returned_value": result
    }
