from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class DatabaseInfoBase(BaseModel):
    name: str
    description: Optional[str] = None


class DatabaseInfoCreate(DatabaseInfoBase):
    pass


class DatabaseInfo(DatabaseInfoBase):
    id: UUID
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class DatabaseInfoList(BaseModel):
    items: list[DatabaseInfo]
    total: int
