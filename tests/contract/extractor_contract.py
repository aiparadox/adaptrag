"""Shared tests that every Extractor implementation must pass.

To test a new extractor, subclass ExtractorContract in a test file and provide
the fixtures: extractor, good_request, missing_request, and optionally
failing_unit_request.
"""

from collections.abc import Iterator

import pytest

from adaptrag.core.elements import Element
from adaptrag.core.ids import element_id
from adaptrag.ports.extractor import ExtractionError, extractor_fingerprint


def run(extractor, request):
    """Run an extractor to the end; return (elements, issues)."""
    elements, issues = [], []
    for item in extractor.extract(request):
        if isinstance(item, Element):
            elements.append(item)
        else:
            issues.append(item)
    return elements, issues


class ExtractorContract:
    """Base class holding the tests; subclasses supply the fixtures."""

    @pytest.fixture
    def extractor(self):
        raise NotImplementedError

    @pytest.fixture
    def good_request(self, tmp_path):
        raise NotImplementedError

    @pytest.fixture
    def missing_request(self, tmp_path):
        raise NotImplementedError

    @pytest.fixture
    def failing_unit_request(self, tmp_path):
        return None

    def test_declares_what_it_is(self, extractor):
        assert extractor.info.name
        assert extractor.info.version
        assert extractor.info.media_types

    def test_supports_the_request_media_type(self, extractor, good_request):
        assert good_request.media_type in extractor.info.media_types

    def test_returns_a_lazy_iterator(self, extractor, good_request):
        assert isinstance(extractor.extract(good_request), Iterator)

    def test_ids_follow_the_deterministic_scheme(self, extractor, good_request):
        elements, _ = run(extractor, good_request)
        fp = extractor_fingerprint(extractor.info, good_request.options)
        expected = [
            element_id(good_request.document_id, fp, i) for i in range(len(elements))
        ]
        assert [e.id for e in elements] == expected

    def test_parents_come_before_children(self, extractor, good_request):
        elements, _ = run(extractor, good_request)
        seen = set()
        for e in elements:
            if e.parent_id is not None:
                assert e.parent_id in seen
            seen.add(e.id)

    def test_same_input_gives_same_output(self, extractor, good_request):
        if not extractor.info.deterministic:
            pytest.skip("extractor declares itself non-deterministic")
        first, _ = run(extractor, good_request)
        second, _ = run(extractor, good_request)
        assert first == second

    def test_missing_source_raises_extraction_error(self, extractor, missing_request):
        with pytest.raises(ExtractionError):
            list(extractor.extract(missing_request))

    def test_bad_unit_is_reported_and_extraction_continues(
        self, extractor, failing_unit_request
    ):
        if failing_unit_request is None:
            pytest.skip("no failing-unit request provided")
        elements, issues = run(extractor, failing_unit_request)
        assert issues
        assert elements
