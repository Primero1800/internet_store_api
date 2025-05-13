from typing import Optional, Any, Annotated

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

from src.tools.phone_number import AppPhoneNumber, app_phonenumber_json_encode

base_address_field = Annotated[str, Field(
        min_length=6,
        max_length=100,
        title="Address",
        description="Customer's address"
    )]

base_city_field = Annotated[str, Field(
        min_length=2,
        max_length=50,
        title="City",
        description="Customer's city"
    )]

base_postcode_field = Annotated[str | None, Field(
        max_length=16,
        title="Postcode",
        description="Customer's postcode",
        default=None
    )]

base_email_field = Annotated[EmailStr | None, Field(
        min_length=6,
        max_length=320,
        title="Email",
        description="Customer's email address",
        default=None
    )]

base_phonenumber_field = Annotated[str, Field(
        min_length=6,
        max_length=20,
        title="Phonenumber",
        description="Customer's phone number",
    )]


class BaseAddress(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            AppPhoneNumber: app_phonenumber_json_encode,
        }
    )

    address: base_address_field
    city: base_city_field
    postcode: base_postcode_field
    email: base_email_field
    phonenumber: base_phonenumber_field


class AddressShort(BaseAddress):
    user_id: int | None


class AddressRead(AddressShort):
    user: Any | None


class AddressCreate(BaseAddress):
    user_id: int | None
    phonenumber: AppPhoneNumber

    @field_validator('phonenumber', mode='before')
    def check_phonenumbern(self, value: Any):
        return AppPhoneNumber.validate(value)


class AddressUpdate(AddressCreate):
    user_id: int | None


class AddressPartialUpdate(AddressCreate):
    user_id: Optional[int] = None
    address: Optional[base_address_field] = None
    city: Optional[base_city_field] = None
    phonenumber: Optional[AppPhoneNumber] = None
