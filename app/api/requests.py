from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str

class HistoryRequest(BaseModel):
    user_id: str