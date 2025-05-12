from pydantic import BaseModel


class CustomTgMessageSchema(BaseModel):
    subject: str = 'Test Message'
    body: str = "Hello! You are reading telegram bot test message"
