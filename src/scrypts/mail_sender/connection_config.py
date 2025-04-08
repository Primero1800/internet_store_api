from fastapi_mail import ConnectionConfig

from src.core.settings import settings


def get_smtp_connection_config():
    return ConnectionConfig(
        MAIL_USERNAME=settings.email.MAIL_USERNAME,
        MAIL_PASSWORD=settings.email.MAIL_PASSWORD,
        MAIL_FROM=settings.email.MAIL_FROM,
        MAIL_PORT=settings.email.MAIL_PORT,
        MAIL_SERVER=settings.email.MAIL_HOST,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )
