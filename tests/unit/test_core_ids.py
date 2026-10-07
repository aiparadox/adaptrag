from adaptrag.core.ids import (
    document_id,
    element_id,
    logical_id,
    sha256_bytes,
    sha256_file,
)


def test_sha256_bytes_known_value():
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256_bytes(b"abc") == expected


def test_sha256_file_matches_bytes(tmp_path):
    data = b"hello" * 100_000
    f = tmp_path / "a.bin"
    f.write_bytes(data)
    assert sha256_file(f) == sha256_bytes(data)


def test_logical_id_is_stable_and_tenant_specific():
    assert logical_id("t1", "file:///a.pdf") == logical_id("t1", "file:///a.pdf")
    assert logical_id("t1", "file:///a.pdf") != logical_id("t2", "file:///a.pdf")


def test_document_id_changes_with_content():
    lg = logical_id("t1", "file:///a.pdf")
    assert document_id(lg, "h1") == document_id(lg, "h1")
    assert document_id(lg, "h1") != document_id(lg, "h2")


def test_parts_are_not_ambiguous():
    assert logical_id("ab", "c") != logical_id("a", "bc")


def test_element_id_depends_on_extractor_and_position():
    assert element_id("doc_x", "fp1", 0) == element_id("doc_x", "fp1", 0)
    assert element_id("doc_x", "fp1", 0) != element_id("doc_x", "fp1", 1)
    assert element_id("doc_x", "fp1", 0) != element_id("doc_x", "fp2", 0)


def test_id_prefixes():
    assert logical_id("t", "s").startswith("lg_")
    assert document_id("lg_x", "h").startswith("doc_")
    assert element_id("doc_x", "fp", 0).startswith("el_")
