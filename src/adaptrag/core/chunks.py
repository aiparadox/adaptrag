"""Chunks: the retrieval units built from elements."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ChunkType(StrEnum):
    """The kind of content a chunk holds."""

    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    SPEECH = "speech"


class Chunk(BaseModel):
    """A retrieval unit built from one or more elements.

    Chunks are derived data. They can be rebuilt from elements at any time, so
    changing the chunking strategy never requires re-parsing the source.
    """

    id: str = Field(min_length=1, description="Deterministic ID (see ids.chunk_id).")
    document_id: str = Field(min_length=1, description="Document version it came from.")
    tenant_id: str = Field(
        min_length=1,
        description="Owner. Copied from the document so search can filter on it.",
    )
    collection: str = Field(
        min_length=1,
        description="Collection within the tenant. Copied for the same reason.",
    )
    chunk_type: ChunkType = Field(
        default=ChunkType.TEXT, description="Kind of content in this chunk."
    )
    element_ids: list[str] = Field(
        min_length=1,
        description=(
            "Elements this chunk was built from, in order. Citations point to "
            "these elements, not to the chunk."
        ),
    )
    embed_text: str = Field(
        min_length=1, description="The text that is turned into a vector."
    )
    display_text: str = Field(
        min_length=1, description="The text shown to a person in results."
    )
    context_text: str | None = Field(
        default=None,
        description="Text placed in the LLM prompt. None means use display_text.",
    )
    token_count: int = Field(ge=0, description="Length of embed_text in tokens.")
    tokenizer: str = Field(
        min_length=1, description="Which tokenizer produced token_count."
    )
    parent_id: str | None = Field(
        default=None, description="Larger chunk (such as the section) around this one."
    )
    previous_id: str | None = Field(
        default=None, description="Chunk before this one in reading order."
    )
    next_id: str | None = Field(
        default=None, description="Chunk after this one in reading order."
    )
    chunker: str = Field(
        min_length=1, description="Fingerprint of the chunker and its settings."
    )
