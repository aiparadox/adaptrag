"""Documents: one ingested file, at one specific version."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1


class Modality(StrEnum):
    """The broad kind of content a document holds."""

    DOCUMENT = "document"
    AUDIO = "audio"


class Document(BaseModel):
    """One ingested file at one version."""

    id: str = Field(
        min_length=1, description="ID of this exact version (see ids.document_id)."
    )
    logical_id: str = Field(
        min_length=1,
        description="ID shared by all versions of the same source (ids.logical_id).",
    )
    tenant_id: str = Field(
        min_length=1,
        description="Owner of the document. Every query is filtered by it.",
    )
    collection: str = Field(
        default="default",
        description="Group within the tenant, such as a project or library.",
    )
    source_uri: str = Field(
        min_length=1, description="Where the file came from, such as a path or URL."
    )
    content_hash: str = Field(
        pattern=r"^[0-9a-f]{64}$",
        description="SHA-256 of the file bytes, as 64 lowercase hex characters.",
    )
    modality: Modality = Field(description="Broad kind of content.")
    media_type: str = Field(description="MIME type, such as 'application/pdf'.")
    title: str | None = Field(default=None, description="Human-readable title.")
    version: int = Field(
        ge=1,
        description="Version number, starting at 1. Assigned by the store.",
    )
    schema_version: int = Field(
        default=SCHEMA_VERSION,
        description="Layout version of this model, used to upgrade old stored data.",
    )
    ext: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Extra metadata with namespaced keys such as 'research.doi', so "
            "purposes can add fields without changing the core."
        ),
    )