"""A fake extractor with canned output.

Used in tests and to try the pipeline without any models.
"""

from collections.abc import Iterator

from adaptrag.core.elements import Element, ElementType
from adaptrag.core.ids import element_id
from adaptrag.core.locators import PageLocator
from adaptrag.ports.extractor import (
    ExtractionError,
    ExtractionIssue,
    ExtractionRequest,
    ExtractorInfo,
    extractor_fingerprint,
)

FAKE_MEDIA_TYPE = "text/x-fake"


class FakeExtractor:
    """Emits a title and a few paragraphs, whatever the file contains.

    Options: `paragraphs` (how many, default 3) and `fail_units` (paragraph
    numbers that should fail, to simulate a bad page).
    """

    info = ExtractorInfo(
        name="fake", version="1", media_types=frozenset({FAKE_MEDIA_TYPE})
    )

    def extract(
        self, request: ExtractionRequest
    ) -> Iterator[Element | ExtractionIssue]:
        """Check the source exists, then return a lazy stream of canned output."""
        if not request.source_path.is_file():
            raise ExtractionError(f"source not found: {request.source_path}")
        return self._generate(request)

    def _generate(
        self, request: ExtractionRequest
    ) -> Iterator[Element | ExtractionIssue]:
        """Produce the canned elements and simulated issues."""
        fingerprint = extractor_fingerprint(self.info, request.options)
        label = f"{self.info.name}@{self.info.version}"
        count = int(request.options.get("paragraphs", 3))
        failing = set(request.options.get("fail_units", []))

        title = Element(
            id=element_id(request.document_id, fingerprint, 0),
            type=ElementType.TITLE,
            text="Fake document",
            locator=PageLocator(page=1),
            extractor=label,
        )
        yield title

        ordinal = 1
        for i in range(count):
            if i in failing:
                yield ExtractionIssue(
                    severity="error", unit=f"paragraph:{i}", message="simulated failure"
                )
                continue
            yield Element(
                id=element_id(request.document_id, fingerprint, ordinal),
                type=ElementType.PARAGRAPH,
                parent_id=title.id,
                order=i,
                text=f"Paragraph {i}.",
                locator=PageLocator(page=1),
                extractor=label,
            )
            ordinal += 1
