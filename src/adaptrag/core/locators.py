from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


class BBox(BaseModel):
    """A rectangle on a page, as fractions of the page size (0 to 1), origin top-left."""

    x0: float = Field(ge=0, le=1)
    y0: float = Field(ge=0, le=1)
    x1: float = Field(ge=0, le=1)
    y1: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _corners_in_order(self) -> Self:
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError("bbox corners are out of order")
        return self


class PageLocator(BaseModel):
    kind: Literal["page"] = "page"
    page: int = Field(ge=1)
    boxes: list[BBox] = Field(default_factory=list)


class TimeLocator(BaseModel):
    kind: Literal["time"] = "time"
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    speaker: str | None = None

    @model_validator(mode="after")
    def _end_not_before_start(self) -> Self:
        if self.end < self.start:
            raise ValueError("end is before start")
        return self


Locator = Annotated[PageLocator | TimeLocator, Field(discriminator="kind")]