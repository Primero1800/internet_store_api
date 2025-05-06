from enum import IntEnum


class PaymentChoices(IntEnum):
    P_WAITS = 0,                                            # Ожидает оплаты / in waiting for payment
    P_PAID = 1,                                                 # Оплачен / already paid
    P_DEL_CASH = 2                                      # Оплата наличными при доставки / cash on delivery
    P_DEL_CARD = 3                                      # Оплата картой при доставке / card on delivery

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]
