from typing import Union
from phonenumbers import (
    PhoneNumber,
    NumberParseException,
    PhoneNumberFormat,
    format_number,
    is_valid_number,
    parse,
    country_code_for_region
)

from src.core.settings import settings
from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Phone Number"


class AppPhoneNumber(PhoneNumber):
    allowed_regions = [country_code_for_region(region) for region in settings.app.APP_ALLOWED_REGIONS]

    @classmethod
    def validate(cls, v: Union[str, 'AppPhoneNumber']) -> 'AppPhoneNumber':
        if not isinstance(v, cls):
            try:
                number = parse(v, None)
            except NumberParseException as ex:
                raise ValueError(f'Invalid phone number: {v}') from ex
        else:
            number = v
        if not is_valid_number(number):
            raise ValueError(f'Invalid phone number: {v}')
        if number.country_code not in cls.allowed_regions:
            raise ValueError(f'Not allowed region: {number.country_code}')
        return cls(**number.__dict__)

    def json_encode(self) -> str:
        return format_number(self, PhoneNumberFormat.E164)


def app_phonenumber_json_encode(number: AppPhoneNumber) -> str:
    return AppPhoneNumber.json_encode(number)
