from typing import Optional, List, Literal,Union
from pydantic import BaseModel, Field
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: Union[str]

class MessageBase(BaseModel):
    messages: List[ChatMessage]
    table_name: Optional[str] = None


class MessageCreate(MessageBase):
    table_name: Optional[str] = None


class Message(MessageBase):
    id: int
    timestamp: datetime
    chat_id: int

    model_config = {
        "from_attributes": True
    }


class ChatBase(BaseModel):
    title: Optional[str] = "New Chat"
    dataset_id: Optional[int] = None
    table_name: Optional[str] = None


class ChatCreate(ChatBase):
    messages: Optional[List[MessageBase]] = None


class Chat(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int
    messages: List[Message] = []

    model_config = {
        "from_attributes": True
    }


class ChatList(BaseModel):
    chats: List[Chat]
    total: int
