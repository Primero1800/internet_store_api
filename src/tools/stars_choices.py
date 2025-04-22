from enum import IntEnum


class StarsChoices(IntEnum):
    S1 = 1              # "Terrible"
    S2 = 2              # "Bad"
    S3 = 3              # "So-so"
    S4 = 4              # "Good"
    S5 = 5              # "Excellent"

    @classmethod
    def choices(cls):
        return [choice.value for choice in cls]
