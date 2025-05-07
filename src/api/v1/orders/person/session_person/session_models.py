from dataclasses import dataclass
from typing import Any, Annotated

from pydantic import Field


@dataclass
class SessionPerson:
    user_id: Annotated[int | None, Field(default=None)]
    user: Annotated[Any | None, Field(default=None)]

    firstname: Annotated[str, Field(min_length=2, max_length=50)]
    lastname: Annotated[str | None, Field(min_length=2, max_length=50, default=None)]
    company_name: Annotated[str | None, Field(min_length=2, max_length=100, default=None)]

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user": self.user,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "company_name": self.company_name,
        }
