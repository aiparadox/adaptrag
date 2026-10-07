import hashlib
from pathlib import Path

_SEP = b"\x1f"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def _make_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(_SEP)
    return f"{prefix}_{h.hexdigest()[:32]}"


def logical_id(tenant_id: str, source_uri: str) -> str:
    return _make_id("lg", tenant_id, source_uri)


def document_id(logical: str, content_hash: str) -> str:
    return _make_id("doc", logical, content_hash)


def element_id(document: str, extractor_fingerprint: str, ordinal: int) -> str:
    return _make_id("el", document, extractor_fingerprint, str(ordinal))