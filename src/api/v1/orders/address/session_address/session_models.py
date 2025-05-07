from dataclasses import dataclass
from typing import Any, Annotated, Optional

from pydantic import Field


@dataclass
class SessionAddress:

    address: Annotated[str, Field(min_length=6, max_length=100)]
    city: Annotated[str, Field(min_length=2, max_length=50)]
    postcode: Annotated[str | None, Field(max_length=16, default=None)]
    email: Annotated[str | None, Field(min_length=6, max_length=320, default=None),]
    phonenumber: Annotated[str, Field(min_length=6, max_length=16)]

    user_id: Optional[int] = None
    user: Optional[Any] = None

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user": self.user,
            "address": self.address,
            "city": self.city,
            "postcode": self.postcode,
            "email": self.email,
            "phonenumber": self.phonenumber,
        }
