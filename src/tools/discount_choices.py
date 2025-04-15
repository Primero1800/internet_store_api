from enum import Enum


class DiscountChoices(Enum):
    D0 = 0              # "без скидки"
    D5 = 5              # "5% скидка"
    D10 = 10        # "10% скидка"
    D15 = 15        # "15% скидка"
    D20 = 20        # "20% скидка"
    D25 = 25        # "25% скидка"
    D30 = 30        # "30% скидка"
    D35 = 35       # "35% скидка"
    D40 = 40        # "40% скидка"
    D45 = 45        # "45% скидка"
    D50 = 50        # "50% скидка"
    D55 = 55        # "55% скидка"
    D60 = 60        # "60% скидка"
    D65 = 65        # "65% скидка"
    D70 = 70        # "70% скидка"

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]