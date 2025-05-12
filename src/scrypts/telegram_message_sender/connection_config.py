from pydantic import BaseModel

from src.core.settings import settings


class TgConnectionConfig(BaseModel):
    token: str = settings.telegram.TELEGRAM_TOKEN
    chat_id: str = settings.telegram.TELEGRAM_CHAT_ID


async def get_tg_connection_config():
    return TgConnectionConfig()
