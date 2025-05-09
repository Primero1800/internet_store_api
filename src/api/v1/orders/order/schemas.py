from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.tools.moveto_choices import MoveToChoices
from src.tools.payment_conditions_choices import PaymentChoices
from src.tools.status_choices import StatusChoices

base_phonenumber_field = Annotated[str, Field(
        min_length=6,
        max_length=20,
        title="Phonenumber",
        description="Customer's phone number",
    )]

base_total_cost_field = Annotated[Decimal, Field(
    max_digits=8,
    decimal_places=2,
    title="Order's total cost"
)]

base_order_content_field = Annotated[list[Any], Field(
    title="Order's content"
)]

base_person_content_field = Annotated[Any, Field(
    title="Order's person"
)]

base_address_content_field = Annotated[Any, Field(
    title="Order's address"
)]

base_time_placed_field = Annotated[datetime, Field(
    title="Order's time of placed"
)]

base_time_delivered_field = Annotated[datetime | None, Field(
    title="Order's time of delivery",
    default=None,
)]

base_move_to_field = Annotated[Literal[*MoveToChoices.choices()], Field(
    title="Order's delivery ways"
)]

base_payment_conditions_field = Annotated[Literal[*PaymentChoices.choices()], Field(
    title="Order's payment conditions"
)]

base_status_field = Annotated[Literal[*StatusChoices.choices()], Field(
    title="Order's status conditions"
)]


class BaseOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[int] = None

    phonenumber: base_phonenumber_field

    order_content: base_order_content_field
    person_content: base_person_content_field
    address_content: base_address_content_field

    move_to: base_move_to_field
    payment_conditions: base_payment_conditions_field
    status: base_status_field


class OrderShort(BaseOrder):
    id: int

    time_placed: base_time_placed_field
    time_delivered: base_time_delivered_field

    total_cost: base_total_cost_field


class OrderRead(OrderShort):
    user: Any


class OrderCreate(BaseOrder):
    time_placed: base_time_placed_field = datetime.now()
    total_cost: base_total_cost_field
    status: base_status_field = StatusChoices.S_ORDERED


class OrderUpdate(OrderCreate):
    time_delivered: base_time_delivered_field


class OrderPartialUpdate(BaseOrder):

    user_id: Optional[int] = None

    phonenumber: Optional[base_phonenumber_field] = None

    order_content: Optional[base_order_content_field] = None
    person_content: Optional[base_person_content_field] = None
    address_content: Optional[base_order_content_field] = None

    move_to: Optional[base_move_to_field] = None
    payment_conditions: Optional[base_payment_conditions_field] = None
    status: Optional[base_status_field] = None

    time_placed: Optional[base_time_placed_field] = None
    time_delivered: Optional[base_time_delivered_field] = None

    total_cost: Optional[base_total_cost_field] = None
