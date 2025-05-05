import abc
from sqlalchemy.ext.asyncio import AsyncSession


class ValidRelationsException(Exception):
    """
    Исключение, генерируемое при обнаружении невалидных отношений.
    """
    pass


class ValidRelationsInspectorBase(abc.ABC):
    """
    Абстрактный базовый класс для инспекторов валидных отношений.

    Классы-наследники должны реализовать метод `inspect`.
    """
    def __init__(self, session: AsyncSession, **kwargs):
        """
        Инициализирует инспектор.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            **kwargs: Дополнительные аргументы для инициализации.
        """
        self.session: AsyncSession = session
        self.need_inspect: list = []
        self.result: dict = {}
        self.error: Exception | None = None

    @abc.abstractmethod
    async def inspect(self) -> dict:
        """
        Асинхронно проверяет валидность отношений.

        Этот метод должен быть реализован в классах-наследниках.
        Возвращает словарь с результатами инспекции.
        Может генерировать ValidRelationsException при обнаружении ошибок.
        """
        raise NotImplementedError
