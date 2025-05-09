from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Order
from src.tools.moveto_choices import MoveToChoices
from src.tools.payment_conditions_choices import PaymentChoices
from src.tools.status_choices import StatusChoices


class OrderFilter(Filter):
    order_by: Optional[list[str]] = ['user_id', 'phonenumber', 'total_cost', 'time_placed', 'time_delivered', 'id']

    total_cost__gte: Optional[Decimal] = Field(default=None, description="Filter by total price greater or equal than", )
    total_cost__lte: Optional[Decimal] = Field(default=None, description="Filter by total price less or equal than", )

    time_placed__gte: Optional[datetime] = Field(default=None, description="Filter by time_placed after or equal than", )
    time_placed__lte: Optional[datetime] = Field(default=None, description="Filter by time_placed before or equal than", )

    time_delivered__gte: Optional[datetime] = Field(
        default=None, description="Filter by time_delivered after or equal than",
    )
    time_delivered__lte: Optional[datetime] = Field(
        default=None, description="Filter by time_delivered before or equal than",
    )

    move_to: Optional[MoveToChoices] = Field(default=None, description="Filter by pick up point")
    payment_conditions: Optional[PaymentChoices] = Field(default=None, description="Filter by payment conditions")
    status: Optional[StatusChoices] = Field(default=None, description="Filter by order's status")

    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = Order
        search_field_name = "search_for"
        search_model_fields = ["phonenumber", "email",]
