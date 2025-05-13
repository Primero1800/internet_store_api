import json

from celery.result import AsyncResult
from fastapi.encoders import jsonable_encoder
from sqlalchemy import event

from src.core.models import Order


CLASS = "Vote"


@event.listens_for(Order, 'after_insert', propagate=True)
def after_order_insert(mapper, connection, target):
    from src.api.v1.celery_tasks.tasks import task_send_tg_message
    result: AsyncResult = task_send_tg_message.apply_async(
        args=(
            {
                'subject': f"{CLASS.upper()} CREATED",
                'body': json.dumps(jsonable_encoder(target.to_dict()), ensure_ascii=False)
            }
        ,))