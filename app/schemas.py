from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    is_admin: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    content_type: str | None
    size_bytes: int
    status: str
    error: str | None
    num_chunks: int
    created_at: datetime


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_ids: list[int] | None = Field(
        default=None, description="Restrict search to these docs"
    )


class Source(BaseModel):
    id: int = Field(description="Citation number used in the answer, e.g. [1]")
    document_id: int
    filename: str
    page: int | None
    chunk_index: int
    score: float = Field(description="Cosine similarity, 0..1")
    snippet: str
    cited: bool = Field(description="True if the answer actually cites this source")


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    model: str
    latency_ms: int
