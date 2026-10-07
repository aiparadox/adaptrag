import re
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from adaptrag.core.locators import Locator

NAMESPACED_TYPE = re.compile(r"^[a-z0-9-]+/[a-z0-9_-]+$")


class ElementType(StrEnum):
    TITLE = "title"
    SECTION_HEADER = "section_header"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    CODE = "code"
    FORMULA = "formula"
    FOOTNOTE = "footnote"
    CAPTION = "caption"
    REFERENCE = "reference"
    TABLE = "table"
    PICTURE = "picture"
    PAGE_HEADER = "page_header"
    PAGE_FOOTER = "page_footer"
    SPEECH_SEGMENT = "speech_segment"
    SPEAKER_TURN = "speaker_turn"
    TOPIC_SECTION = "topic_section"
    DESCRIPTION = "description"
    SUMMARY = "summary"


class Origin(StrEnum):
    EXTRACTED = "extracted"
    GENERATED = "generated"


CORE_TYPES = {t.value for t in ElementType}


class Element(BaseModel):
    id: str = Field(min_length=1)
    type: str
    parent_id: str | None = None
    order: int = Field(default=0, ge=0)
    text: str | None = None
    locator: Locator | None = None
    language: str | None = None
    origin: Origin = Origin.EXTRACTED
    quality: float | None = Field(default=None, ge=0, le=1)
    extractor: str | None = None

    @field_validator("type")
    @classmethod
    def _core_or_namespaced(cls, value: str) -> str:
        if value in CORE_TYPES or NAMESPACED_TYPE.match(value):
            return value
        raise ValueError(f"unknown element type: {value!r}")