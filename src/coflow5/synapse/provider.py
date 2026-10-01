from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DraftRequest:
    request_id: str
    question: str
    event_id: str
    accepted_action: str
    reason_code: str
    citation_chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class DraftAnswer:
    answer: str
    event_id: str
    accepted_action: str
    reason_code: str
    citation_chunk_ids: tuple[str, ...]


class OptionalDraftProvider(Protocol):
    """Optional in-process drafting boundary; callers verify every returned field."""

    def draft(self, request: DraftRequest) -> DraftAnswer: ...
