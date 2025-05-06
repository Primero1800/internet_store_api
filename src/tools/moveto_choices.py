from enum import IntEnum


class MoveToChoices(IntEnum):
    TO_PICKUP_POINT = 0,                        # Пункт выдачи / Pickup point
    TO_CUSTOMER_ADDRESS = 1,          # Адрес заказчика / Customer address

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]