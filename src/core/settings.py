import logging
from pathlib import Path
from typing import Literal

from src.tools import BaseCustomSettings


# /**/4_el/src
BASE_DIR = Path(__file__).resolve().parent.parent


class CustomSettings(BaseCustomSettings):
    pass


CustomSettings.set_app_name_as_source(
    ('src',)
)


class AppSettings(CustomSettings):
    APP_BASE_DIR: str = str(BASE_DIR)
    APP_NAME: str
    APP_TITLE: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    APP_TIMEZONE: str
    APP_ALLOWED_REGIONS: list = ["RU", "BY", "UZ"]

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


class Auth(CustomSettings):
    AUTH_TOKEN_LIFETIME: int

    AUTH_PRIVATE_KEY: Path = BASE_DIR / "core" / "certs" / "jwt-private.pem"
    AUTH_PUBLIC_KEY: Path = BASE_DIR / "core" / "certs" / "jwt-public.pem"

    AUTH_RESET_PASSWORD_TOKEN_SECRET: str
    AUTH_VERIFICATION_TOKEN_SECRET: str

    AUTH_VERIFICATION_TOKEN_LIFETIME_SECONDS: int
    AUTH_RESET_PASSWORD_TOKEN_LIFETIME_SECONDS: int

    def get_url(selfself, purpose: str, version: str = "v1"):
        PURPOSE = ''
        SECOND_PARAM = "unversioned"

        if version == "v1":
            SECOND_PARAM = settings.app.API_V1_PREFIX
        if purpose == "transport-token":
            PURPOSE = "login"
        elif purpose in (
            "request-verify-token",
            "verify",
            "verify-hook",
            "reset-password",
            "reset-password-hook"
        ):
            PURPOSE = purpose
        return "{}{}{}/{}".format(
            settings.app.API_PREFIX,
            SECOND_PARAM,
            settings.tags.AUTH_PREFIX,
            PURPOSE,
        )


class Carts(CustomSettings):
    SUMMARY_POLICY_AFTER_LOGIN: bool = False


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


class Email(CustomSettings):
    MAIL_HOST: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_FROM: str


class LoggingConfig(CustomSettings):
    LOGGING_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    LOGGING_FORMAT: str
    LOGGER: logging.Logger = logging.getLogger(__name__)

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.LOGGING_LEVEL]


class RateLimiter(CustomSettings):
    RATE_LIMITER_CALLS: int
    RATE_LIMITER_PERIOD: int


class RedisConf(CustomSettings):
    REDIS_HOST: str
    REDIS_DATABASE: int
    REDIS_PORT: int = 6379
    REDIS_CACHE_LIFETIME_SECONDS: int = 3600 * 24

    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:6379/{self.REDIS_DATABASE_1}"


class RunConfig(CustomSettings):
    app_src: AppRunConfig = AppRunConfig()


class Sessions(CustomSettings):
    SESSIONS_MAX_AGE: int
    SESSIONS_SECRET_KEY: str
    SESSION_CART: str
    SESSION_PERSON: str
    SESSION_ADDRESS: str


class Tags(CustomSettings):
    TECH_TAG: str
    ROOT_TAG: str
    SWAGGER_TAG: str

    USERS_PREFIX: str
    USERS_TAG: str

    USERTOOLS_PREFIX: str
    USERTOOLS_TAG: str

    AUTH_PREFIX: str
    AUTH_TAG: str

    SESSIONS_PREFIX: str
    SESSIONS_TAG: str

    BRANDS_PREFIX: str
    BRANDS_TAG: str

    RUBRICS_PREFIX: str
    RUBRICS_TAG: str

    PRODUCTS_PREFIX: str
    PRODUCTS_TAG: str

    ADD_INFO_PREFIX: str
    ADD_INFO_TAG: str

    SALE_INFO_PREFIX: str
    SALE_INFO_TAG: str

    VOTES_PREFIX: str
    VOTES_TAG: str

    POSTS_PREFIX: str
    POSTS_TAG: str

    CARTS_PREFIX: str
    CARTS_TAG: str

    ORDERS_PREFIX: str
    ORDERS_TAG: str

    PERSONS_PREFIX: str
    PERSONS_TAG: str

    ADDRESSES_PREFIX: str
    ADDRESSES_TAG: str


class Users(CustomSettings):
    USERS_PASSWORD_MIN_LENGTH: int


class Settings(CustomSettings):
    app: AppSettings = AppSettings()
    carts: Carts = Carts()
    logging: LoggingConfig = LoggingConfig()
    run: RunConfig = RunConfig()
    tags: Tags = Tags()
    db: DB = DB()
    auth: Auth = Auth()
    users: Users = Users()
    email: Email = Email()
    rate_limiter: RateLimiter = RateLimiter()
    redis: RedisConf = RedisConf()
    sessions: Sessions = Sessions()


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
