from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PARSER_VERSION = "plain-text-paragraph-v1"
CHUNKER_VERSION = "stable-content-hash-v1"
RETRIEVAL_VERSION = "deterministic-exact-token-v1"


class CorpusValidationError(ValueError):
    pass


class RetrievalUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class CorpusSource:
    source_id: str
    path: str
    sha256: str
    evidence_class: str


@dataclass(frozen=True)
class CorpusChunk:
    chunk_id: str
    source_id: str
    source_path: str
    source_sha256: str
    evidence_class: str
    ordinal: int
    content: str
    content_sha256: str
    parser_version: str = PARSER_VERSION
    chunker_version: str = CHUNKER_VERSION


@dataclass(frozen=True)
class RetrievalHit:
    chunk: CorpusChunk
    matched_tokens: tuple[str, ...]
    score: int

    def citation(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "source_id": self.chunk.source_id,
            "source_path": self.chunk.source_path,
            "source_sha256": self.chunk.source_sha256,
            "evidence_class": self.chunk.evidence_class,
            "matched_tokens": list(self.matched_tokens),
        }


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def exact_tokens(value: str) -> tuple[str, ...]:
    return tuple(sorted(set(TOKEN_RE.findall(value.lower()))))


class ExactTokenCorpus:
    """A read-only retriever over the exact source allow-list sealed in a contract."""

    def __init__(self, root: Path, sources: Mapping[str, CorpusSource], *, available: bool = True) -> None:
        self._root = root.resolve()
        self._sources = dict(sources)
        self._available = available
        self._chunks = tuple(
            chunk
            for source_id in sorted(self._sources)
            for chunk in self.ingest_source(
                source_id,
                self._sources[source_id].path,
                self._sources[source_id].sha256,
            )
        )
        self._by_id = {chunk.chunk_id: chunk for chunk in self._chunks}
        if len(self._by_id) != len(self._chunks):
            raise CorpusValidationError("stable chunk identity collision")

    @classmethod
    def from_contract(cls, root: Path, contract_path: Path, *, available: bool = True) -> "ExactTokenCorpus":
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        sources = {
            source_id: CorpusSource(
                source_id=source_id,
                path=value["path"],
                sha256=value["sha256"],
                evidence_class=value["evidence_class"],
            )
            for source_id, value in contract["corpus"]["sources"].items()
        }
        return cls(root, sources, available=available)

    @property
    def chunks(self) -> tuple[CorpusChunk, ...]:
        return self._chunks

    @property
    def sources(self) -> tuple[CorpusSource, ...]:
        return tuple(self._sources[key] for key in sorted(self._sources))

    def chunk(self, chunk_id: str) -> CorpusChunk | None:
        return self._by_id.get(chunk_id)

    def ingest_source(self, source_id: str, path: str, expected_hash: str) -> tuple[CorpusChunk, ...]:
        allowed = self._sources.get(source_id)
        if allowed is None:
            raise CorpusValidationError(f"source is outside sealed allow-list: {source_id}")
        if path != allowed.path or expected_hash != allowed.sha256 or not HASH_RE.fullmatch(expected_hash):
            raise CorpusValidationError(f"path or hash differs from sealed allow-list: {source_id}")
        source_path = (self._root / path).resolve()
        try:
            source_path.relative_to(self._root)
        except ValueError as exc:
            raise CorpusValidationError("source path escapes repository root") from exc
        actual_hash = sha256_file(source_path)
        if actual_hash != expected_hash:
            raise CorpusValidationError(f"source content hash mismatch: {source_id}")
        normalized = source_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        paragraphs = [part.strip() for part in re.split(r"\n[ \t]*\n+", normalized) if part.strip()]
        chunks: list[CorpusChunk] = []
        occurrences: dict[str, int] = {}
        for ordinal, content in enumerate(paragraphs):
            content_hash = sha256_bytes(content.encode("utf-8"))
            occurrence = occurrences.get(content_hash, 0)
            occurrences[content_hash] = occurrence + 1
            identity = sha256_bytes(f"{source_id}\0{content}\0{occurrence}".encode("utf-8"))
            chunks.append(CorpusChunk(
                chunk_id="chunk-" + identity.removeprefix("sha256:"),
                source_id=source_id,
                source_path=path,
                source_sha256=actual_hash,
                evidence_class=allowed.evidence_class,
                ordinal=ordinal,
                content=content,
                content_sha256=content_hash,
            ))
        return tuple(chunks)

    def search(self, query: str, *, limit: int = 5) -> tuple[RetrievalHit, ...]:
        if not self._available:
            raise RetrievalUnavailable("sealed local retrieval is unavailable")
        if limit < 1:
            raise ValueError("limit must be positive")
        query_tokens = set(exact_tokens(query))
        if not query_tokens:
            return ()
        hits: list[RetrievalHit] = []
        for chunk in self._chunks:
            matched = tuple(sorted(query_tokens & set(exact_tokens(chunk.content))))
            if matched:
                hits.append(RetrievalHit(chunk=chunk, matched_tokens=matched, score=len(matched)))
        hits.sort(key=lambda hit: (-hit.score, hit.chunk.source_id, hit.chunk.ordinal, hit.chunk.chunk_id))
        return tuple(hits[:limit])
