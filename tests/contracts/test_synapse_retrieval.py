from __future__ import annotations

from pathlib import Path

import pytest

from coflow5.synapse import CorpusValidationError, ExactTokenCorpus

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "harness/work/12-synapse-agents/contract.json"


def test_allowlisted_ingestion_records_identity_versions_and_hashes() -> None:
    corpus = ExactTokenCorpus.from_contract(ROOT, CONTRACT)
    assert {source.source_id for source in corpus.sources} == {"adr-0001", "course-brief", "requirements", "design"}
    assert corpus.chunks
    assert all(chunk.chunk_id.startswith("chunk-") and len(chunk.chunk_id) == 70 for chunk in corpus.chunks)
    assert all(chunk.parser_version == "plain-text-paragraph-v1" for chunk in corpus.chunks)
    assert all(chunk.chunker_version == "stable-content-hash-v1" for chunk in corpus.chunks)
    assert all(chunk.source_sha256.startswith("sha256:") for chunk in corpus.chunks)


def test_reingestion_is_stable_and_outside_path_or_hash_fails_closed() -> None:
    first = ExactTokenCorpus.from_contract(ROOT, CONTRACT)
    second = ExactTokenCorpus.from_contract(ROOT, CONTRACT)
    assert [chunk.chunk_id for chunk in first.chunks] == [chunk.chunk_id for chunk in second.chunks]
    source = first.sources[0]
    with pytest.raises(CorpusValidationError, match="path or hash"):
        first.ingest_source(source.source_id, "README.md", source.sha256)
    with pytest.raises(CorpusValidationError, match="path or hash"):
        first.ingest_source(source.source_id, source.path, "sha256:" + "0" * 64)
    with pytest.raises(CorpusValidationError, match="outside sealed allow-list"):
        first.ingest_source("not-allowed", source.path, source.sha256)


def test_exact_token_ranking_and_citations_are_deterministic() -> None:
    corpus = ExactTokenCorpus.from_contract(ROOT, CONTRACT)
    first = corpus.search("Synapse actuation Max-Pressure safety control")
    second = corpus.search("Synapse actuation Max-Pressure safety control")
    assert first and first == second
    assert [hit.score for hit in first] == sorted((hit.score for hit in first), reverse=True)
    assert any(hit.chunk.source_id == "adr-0001" for hit in first)
    assert all(hit.matched_tokens and hit.citation()["source_sha256"] == hit.chunk.source_sha256 for hit in first)
    assert corpus.search("zzzxxyy token-with-no-corpus-match") == ()
