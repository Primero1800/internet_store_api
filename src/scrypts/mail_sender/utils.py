from logging import Logger, getLogger
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema

from src.api.v1.message_senders import CustomMessageSchema


logger = getLogger(__name__)


def get_message_params(schema: CustomMessageSchema):
    return MessageSchema(**schema.model_dump(), subtype='html')


async def send_mail(
        schema: CustomMessageSchema,
        background_tasks: BackgroundTasks = None,
        logger: Logger = logger
) -> bool:

    from .connection_config import get_smtp_connection_config

    message = get_message_params(schema)
    fm = FastMail(get_smtp_connection_config())

    if background_tasks:
        try:
            background_tasks.add_task(fm.send_message, message, )
            logger.info("Starting mailsender as background task")
            return True
        except Exception as exc:
            logger.error(f"Mailsender as background task error: {exc}")
            return False
    else:
        try:
            await fm.send_message(message=message)
            logger.info("Starting mailsender as async task")
            return True
        except Exception as exc:
            logger.error(f"Mailsender as async task error: {exc}")
            return False

    # ClientConnectorDNSError
