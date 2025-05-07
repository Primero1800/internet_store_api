from typing import Optional, Any, Annotated

from pydantic import BaseModel, ConfigDict, Field

base_firstname_field = Annotated[str, Field(
        min_length=2,
        max_length=50,
        title="Firstname",
        description="Person's firstname"
    )]

base_lastname_field = Annotated[str | None, Field(
        min_length=2,
        max_length=50,
        title="Lastname",
        description="Person's lastname"
    )]

base_company_name_field = Annotated[str | None, Field(
        min_length=2,
        max_length=100,
        title="Company name",
        description="Person's company name"
    )]


class BasePerson(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    firstname: base_firstname_field
    lastname: base_lastname_field
    company_name: base_company_name_field


class PersonShort(BasePerson):
    user_id: int | None


class PersonRead(PersonShort):
    user: Any | None


class PersonCreate(BasePerson):
    pass


class PersonUpdate(PersonCreate):
    pass


class PersonPartialUpdate(PersonCreate):
    firstname: Optional[base_firstname_field]
