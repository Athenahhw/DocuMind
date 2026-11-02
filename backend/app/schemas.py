
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    filename: str = Field(min_length=1, max_length=255)
    file_path: str
    file_type: str = Field(min_length=1, max_length=20)
    category_id: int | None = None


class DocumentResponse(DocumentCreate):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
