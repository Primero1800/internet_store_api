from enum import IntEnum


class CustomerPaymentChoices(IntEnum):
    P_IN_ADVANCE = 0,                                    # Предоплата / in advance payment
    P_DEL_CASH = 2                                      # Оплата наличными при доставки / cash on delivery
    P_DEL_CARD = 3                                      # Оплата картой при доставке / card on delivery

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]
