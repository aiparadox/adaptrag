import pytest
from pydantic import ValidationError

from adaptrag.core.chunks import Chunk, ChunkType


def make(**overrides):
    base = {
        "id": "ch_1",
        "document_id": "doc_1",
        "tenant_id": "t1",
        "collection": "default",
        "element_ids": ["el_1"],
        "embed_text": "Some text.",
        "display_text": "Some text.",
        "token_count": 3,
        "tokenizer": "approx",
        "chunker": "fp1",
    }
    base.update(overrides)
    return Chunk(**base)


def test_chunk_defaults():
    c = make()
    assert c.chunk_type is ChunkType.TEXT
    assert c.context_text is None
    assert c.parent_id is None
    assert c.previous_id is None
    assert c.next_id is None


def test_chunk_needs_at_least_one_element():
    with pytest.raises(ValidationError):
        make(element_ids=[])


def test_chunk_needs_text():
    with pytest.raises(ValidationError):
        make(embed_text="")
    with pytest.raises(ValidationError):
        make(display_text="")


def test_token_count_not_negative():
    with pytest.raises(ValidationError):
        make(token_count=-1)


def test_chunk_json_round_trip():
    c = make(chunk_type=ChunkType.TABLE, parent_id="ch_0", element_ids=["a", "b"])
    assert Chunk.model_validate_json(c.model_dump_json()) == c
