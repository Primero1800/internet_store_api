from enum import IntEnum


class StatusChoices(IntEnum):
    S_ORDERED = 0                           # Заказан / ordered
    S_DELIVERED = 1                         # Доставлен / delivered
    S_CANCELLED = 2                         # Отменен / cancelled

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]
