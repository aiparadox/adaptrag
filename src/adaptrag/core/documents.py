from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1


class Modality(StrEnum):
    DOCUMENT = "document"
    AUDIO = "audio"


class Document(BaseModel):
    id: str = Field(min_length=1)
    logical_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    collection: str = "default"
    source_uri: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    modality: Modality
    media_type: str
    title: str | None = None
    version: int = Field(ge=1)
    schema_version: int = SCHEMA_VERSION
    ext: dict[str, Any] = Field(default_factory=dict)