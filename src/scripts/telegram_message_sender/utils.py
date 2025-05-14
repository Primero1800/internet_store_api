from logging import Logger, getLogger
from typing import TYPE_CHECKING

import telegram
from fastapi import BackgroundTasks

from src.api.v1.message_senders import CustomTgMessageSchema

if TYPE_CHECKING:
    from src.scripts.telegram_message_sender.connection_config import TgConnectionConfig

logger = getLogger(__name__)


async def compose_message(
        schema: CustomTgMessageSchema
):
    return f"{schema.subject.upper()}: {schema.body}"


async def send_message(
        message: str,
        config: "TgConnectionConfig",
):
    """
    Асинхронная функция для отправки сообщения в ТГ.
    """
    try:
        bot = telegram.Bot(
            token=config.token
        )
        chat_id = config.chat_id
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as exc:
        raise exc


async def send_tg_bot_message(
        schema: CustomTgMessageSchema,
        background_tasks: BackgroundTasks = None,
        logger: Logger = logger
) -> bool:

    from .connection_config import get_tg_connection_config
    tg_config = await get_tg_connection_config()
    message = await compose_message(schema)

    if background_tasks:
        try:
            background_tasks.add_task(
                send_message,
                message, tg_config
            )
            logger.info("Starting telegram sender as background task")
            return True
        except Exception as exc:
            logger.error(f"Telegram sender as background task error: {exc}")
            return False
    else:
        try:
            await send_message(
                message=message,
                config=tg_config,
            )
            logger.info("Starting telegram sender as async task")
            return True
        except Exception as exc:
            logger.error(f"Telegram sender as async task error: {exc}")
            return False

    #
