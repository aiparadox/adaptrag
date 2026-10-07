"""Content hashing and deterministic IDs.

The same input always gives the same ID. That is what makes re-ingesting an
unchanged file a no-op and keeps old citations resolvable.
"""

import hashlib
from pathlib import Path

_SEP = b"\x1f"


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of the given bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file.

    The file is read in 1 MB blocks, so large files do not fill memory.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def _make_id(prefix: str, *parts: str) -> str:
    """Build a prefixed, deterministic ID from the given parts.

    A separator byte follows each part, so ("ab", "c") and ("a", "bc") give
    different IDs. The result is the prefix plus 32 hex characters (128 bits).
    """
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(_SEP)
    return f"{prefix}_{h.hexdigest()[:32]}"


def logical_id(tenant_id: str, source_uri: str) -> str:
    """Return the ID of a document across all of its versions.

    The same tenant and source always give the same ID.
    """
    return _make_id("lg", tenant_id, source_uri)


def document_id(logical: str, content_hash: str) -> str:
    """Return the ID of one version of a document.

    It is built from the logical ID and the content hash, so identical content
    gives the identical ID and changed content gives a new one.
    """
    return _make_id("doc", logical, content_hash)


def element_id(document: str, extractor_fingerprint: str, ordinal: int) -> str:
    """Return the ID of one element.

    It is built from the document version, the extractor fingerprint and the
    element's position, so two extractors on the same file never collide.
    """
    return _make_id("el", document, extractor_fingerprint, str(ordinal))
