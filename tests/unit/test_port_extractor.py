import pytest
from pydantic import ValidationError

from adaptrag.ports.extractor import ExtractorInfo, extractor_fingerprint


def make_info(version="1"):
    return ExtractorInfo(name="x", version=version, media_types=frozenset({"a/b"}))


def test_fingerprint_ignores_option_order():
    a = extractor_fingerprint(make_info(), {"a": 1, "b": 2})
    b = extractor_fingerprint(make_info(), {"b": 2, "a": 1})
    assert a == b


def test_fingerprint_changes_with_options_and_version():
    base = extractor_fingerprint(make_info(), {"a": 1})
    assert base != extractor_fingerprint(make_info(), {"a": 2})
    assert base != extractor_fingerprint(make_info("2"), {"a": 1})


def test_info_needs_a_media_type():
    with pytest.raises(ValidationError):
        ExtractorInfo(name="x", version="1", media_types=frozenset())
