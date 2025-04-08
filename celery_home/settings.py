from src.tools import BaseCustomSettings


class CustomSettings(BaseCustomSettings):
    pass


CustomSettings.set_app_name_as_source(
    ("celery_home", "src",)
)


class CeleryCustom(CustomSettings):
    APP_NAME: str
    CELERY_BROKER: str
    CELERY_RESULT: str
    CELERY_BROKER_HOST: str
    CELERY_RESULT_EXPIRES_DAYS: int
    CELERY_RESULT_EXPIRES_HOURS: int
    APP_TIMEZONE: str

    @property
    def CELERY_BROKER_URL(self):
        return f"{self.CELERY_BROKER}://{self.CELERY_BROKER_HOST}:6379/0"

    @property
    def CELERY_BROKER_BACKEND(self):
        return f"{self.CELERY_BROKER}://{self.CELERY_BROKER_HOST}:6379/0"


class Settings(CustomSettings):
    celery: CeleryCustom = CeleryCustom()


settings = Settings()
