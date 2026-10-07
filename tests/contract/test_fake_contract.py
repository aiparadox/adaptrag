import pytest
from extractor_contract import ExtractorContract

from adaptrag.adapters.fake_extractor import FAKE_MEDIA_TYPE, FakeExtractor
from adaptrag.ports.extractor import ExtractionRequest


def make_request(path, **options):
    return ExtractionRequest(
        source_path=path,
        media_type=FAKE_MEDIA_TYPE,
        tenant_id="t1",
        document_id="doc_1",
        options=options,
    )


def make_file(tmp_path):
    f = tmp_path / "a.fake"
    f.write_text("x")
    return f


class TestFakeExtractor(ExtractorContract):
    @pytest.fixture
    def extractor(self):
        return FakeExtractor()

    @pytest.fixture
    def good_request(self, tmp_path):
        return make_request(make_file(tmp_path))

    @pytest.fixture
    def missing_request(self, tmp_path):
        return make_request(tmp_path / "nope.fake")

    @pytest.fixture
    def failing_unit_request(self, tmp_path):
        return make_request(make_file(tmp_path), paragraphs=3, fail_units=[1])


def test_paragraph_count_option(tmp_path):
    request = make_request(make_file(tmp_path), paragraphs=5)
    assert len(list(FakeExtractor().extract(request))) == 6  # title + 5
