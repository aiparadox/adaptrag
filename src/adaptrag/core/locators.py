"""Locators: where a piece of content came from in its source."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator


class BBox(BaseModel):
    """A rectangle on a page.

    Coordinates are fractions of the page size (0 to 1) with the origin at the
    top-left corner, so they do not depend on resolution or PDF point units.
    """

    x0: float = Field(ge=0, le=1, description="Left edge.")
    y0: float = Field(ge=0, le=1, description="Top edge.")
    x1: float = Field(ge=0, le=1, description="Right edge. Not less than x0.")
    y1: float = Field(ge=0, le=1, description="Bottom edge. Not less than y0.")

    @model_validator(mode="after")
    def _corners_in_order(self) -> Self:
        """Reject rectangles whose corners are flipped."""
        if self.x1 < self.x0 or self.y1 < self.y0:
            raise ValueError("bbox corners are out of order")
        return self


class PageLocator(BaseModel):
    """Points to a region of a page in a PDF or other paged document."""

    kind: Literal["page"] = Field(
        default="page", description="Tag that identifies this locator type."
    )
    page: int = Field(ge=1, description="Page number, starting at 1.")
    boxes: list[BBox] = Field(
        default_factory=list,
        description="Regions on the page. Empty when the parser gives no positions.",
    )


class TimeLocator(BaseModel):
    """Points to a time range in audio or video."""

    kind: Literal["time"] = Field(
        default="time", description="Tag that identifies this locator type."
    )
    start: float = Field(ge=0, description="Start, in seconds from the beginning.")
    end: float = Field(ge=0, description="End, in seconds. Not before start.")
    speaker: str | None = Field(
        default=None, description="Speaker label, if speakers were identified."
    )

    @model_validator(mode="after")
    def _end_not_before_start(self) -> Self:
        """Reject ranges that end before they start."""
        if self.end < self.start:
            raise ValueError("end is before start")
        return self


# A locator is either kind; the `kind` field says which one it is.
Locator = Annotated[PageLocator | TimeLocator, Field(discriminator="kind")]