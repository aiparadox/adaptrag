"""The extractor port: the contract for turning a source file into elements."""

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from adaptrag.core.elements import Element
from adaptrag.core.ids import sha256_bytes


class ExtractionError(Exception):
    """Raised when a whole source cannot be extracted, such as a missing file."""


class ExtractorInfo(BaseModel):
    """What an extractor is and what it can do."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, description="Short unique name of the extractor.")
    version: str = Field(min_length=1, description="Version of the extractor.")
    media_types: frozenset[str] = Field(
        min_length=1, description="MIME types this extractor can read."
    )
    features: frozenset[str] = Field(
        default_factory=frozenset,
        description="Capabilities such as 'tables' or 'ocr'.",
    )
    deterministic: bool = Field(
        default=True,
        description="False if the same input may give different output (OCR, ASR).",
    )
    vram_mb: int = Field(
        default=0, ge=0, description="Approximate GPU memory needed, in megabytes."
    )


class ExtractionRequest(BaseModel):
    """Everything an extractor receives: the source, who owns it, and options."""

    source_path: Path = Field(description="Path of the file to extract.")
    media_type: str = Field(description="MIME type of the file.")
    tenant_id: str = Field(min_length=1, description="Owner of the document.")
    document_id: str = Field(min_length=1, description="ID of this document version.")
    options: dict[str, Any] = Field(
        default_factory=dict, description="Extractor-specific settings."
    )


class ExtractionIssue(BaseModel):
    """A problem found during extraction that did not stop it."""

    severity: Literal["warning", "error"] = Field(description="How serious it is.")
    unit: str | None = Field(
        default=None, description="Where it happened, such as 'page:37'."
    )
    message: str = Field(description="What went wrong.")


class Extractor(Protocol):
    """Turns a source file into a stream of elements and issues.

    A problem with a single unit (one page, one segment) is yielded as an
    ExtractionIssue and extraction continues. A problem with the whole source
    raises ExtractionError.
    """

    info: ExtractorInfo

    def extract(
        self, request: ExtractionRequest
    ) -> Iterator[Element | ExtractionIssue]:
        """Yield elements and issues one at a time, in document order."""
        ...


def extractor_fingerprint(info: ExtractorInfo, options: Mapping[str, Any]) -> str:
    """Return a short fingerprint of an extractor's identity and options.

    The same extractor, version and options always give the same fingerprint,
    whatever order the options are written in.
    """
    payload = json.dumps(
        {"name": info.name, "version": info.version, "options": options},
        sort_keys=True,
        default=str,
    )
    return sha256_bytes(payload.encode("utf-8"))[:16]
