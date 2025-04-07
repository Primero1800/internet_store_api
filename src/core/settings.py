from src.tools.classes import BaseCustomSettings


class CustomSettings(BaseCustomSettings):
    pass


CustomSettings.set_app_name_as_source(
    ('app1',)
)


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