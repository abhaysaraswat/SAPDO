from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "CSV"  # CSV, JSON, etc.
    database_info_id: Optional[UUID] = None
    table_name: Optional[str] = None


class DatasetCreate(DatasetBase):
    pass


class DatabaseInfo(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    table_name: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
    #hi


class Dataset(DatasetBase):
    id: Any  # Accept any type for id (UUID string or int)
    created_at: datetime
    updated_at: datetime
    number_of_datapoints: int = 0
    number_of_experiments: int = 0
    number_of_optimizations: int = 0
    derived_datasets: int = 0
    owner_id: int
    database_info: Optional[DatabaseInfo] = None

    model_config = {
        "from_attributes": True
    }


class DatasetList(BaseModel):
    datasets: List[Dataset]
    total: int
