import logging
import os
import sys
from pathlib import Path
from typing import Literal

from src.tools import BaseCustomSettings


class CustomSettings(BaseCustomSettings):
    pass


CustomSettings.set_app_name_as_source(
    ('src',)
)


class AppSettings(CustomSettings):
    # /home/primero/Python/python_codes/fastapi/4_el/src
    APP_BASE_DIR: str = str(Path(__file__).resolve().parent.parent)
    APP_TITLE: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    APP_TIMEZONE: str

    API_PREFIX: str
    API_V1_PREFIX: str


class AppRunConfig(CustomSettings):
    APP_PATH: str
    APP_HOST: str
    APP_PORT: int
    APP_RELOAD: bool

    APP_HOST_SERVER_TO_PLACE: str = ''
    APP_HOST_PROTOCOL_TO_PLACE: str = 'http'

    @property
    def APP_HOST_SERVER_URL(self):
        if self.APP_HOST_SERVER_TO_PLACE:
            return f"{self.APP_HOST_PROTOCOL_TO_PLACE}://{self.APP_HOST_SERVER_TO_PLACE}"
        return f"{self.APP_HOST_PROTOCOL_TO_PLACE}://{self.APP_HOST}:{self.APP_PORT}"


class DB(CustomSettings):

    # DB_NAME: str = os.getenv('DB_NAME_TEST') if 'pytest' in sys.modules else os.getenv('DB_NAME')
    DB_NAME_TEST: str
    DB_NAME: str
    DB_ENGINE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    DB_TABLE_PREFIX: str

    DB_ECHO_MODE: bool
    DB_POOL_SIZE: int

    DB_URL: str = ''
    DB_TEST_URL: str = ''

    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }


class LoggingConfig(CustomSettings):
    LOGGING_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    LOGGING_FORMAT: str
    LOGGER: logging.Logger = logging.getLogger(__name__)

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.LOGGING_LEVEL]


class RunConfig(CustomSettings):
    app_src: AppRunConfig = AppRunConfig()


class Tags(CustomSettings):
    TECH_TAG: str
    ROOT_TAG: str
    SWAGGER_TAG: str


class Settings(CustomSettings):
    app: AppSettings = AppSettings()
    logging: LoggingConfig = LoggingConfig()
    run: RunConfig = RunConfig()
    tags: Tags = Tags()
    db: DB = DB()


settings = Settings()


def get_db_connection(db_name: str) -> str:
    return '{}://{}:{}@{}:{}/{}'.format(
        settings.db.DB_ENGINE,
        settings.db.DB_USER,
        settings.db.DB_PASSWORD,
        settings.db.DB_HOST,
        settings.db.DB_PORT,
        db_name,
    )


settings.db.DB_URL = get_db_connection(settings.db.DB_NAME)
settings.db.DB_TEST_URL = get_db_connection(settings.db.DB_NAME_TEST)
