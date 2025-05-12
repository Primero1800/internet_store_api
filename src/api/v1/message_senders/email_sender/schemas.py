from typing import List

from pydantic import BaseModel


class CustomMessageSchema(BaseModel):
    recipients: List[str] = ['admin@primero1800.store', 'primero@inbox.ru', ]
    subject: str = 'Test Message'
    body: str = "Hello! You are reading test message"
