import logging
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


settings = Settings()
