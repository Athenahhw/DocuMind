
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
    content: str | None = None
    page_count: int | None = None


class DocumentContentResponse(BaseModel):
    id: int
    title: str
    content: str | None
    page_count: int | None

    model_config = ConfigDict(from_attributes=True)

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str

    model_config = ConfigDict(from_attributes=True)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: int | None = None


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResult]


class AskRequest(BaseModel):
    question: str
    top_k: int = 5
    document_id: int | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult]
