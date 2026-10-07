import pytest
from pydantic import ValidationError

from adaptrag.core.documents import SCHEMA_VERSION, Document, Modality


def make(**overrides):
    base = {
        "id": "doc_1",
        "logical_id": "lg_1",
        "tenant_id": "t1",
        "source_uri": "file:///a.pdf",
        "content_hash": "a" * 64,
        "modality": Modality.DOCUMENT,
        "media_type": "application/pdf",
        "version": 1,
    }
    base.update(overrides)
    return Document(**base)


def test_document_defaults():
    d = make()
    assert d.collection == "default"
    assert d.schema_version == SCHEMA_VERSION
    assert d.title is None
    assert d.ext == {}


def test_tenant_required():
    with pytest.raises(ValidationError):
        make(tenant_id="")


def test_version_starts_at_one():
    with pytest.raises(ValidationError):
        make(version=0)


def test_content_hash_must_be_sha256_hex():
    with pytest.raises(ValidationError):
        make(content_hash="xyz")


def test_json_round_trip():
    d = make(title="Policy", ext={"research.doi": "10.1/x"})
    assert Document.model_validate_json(d.model_dump_json()) == d
