from __future__ import annotations

STATUS = {
    "not_found": 404,
    "validation": 422,
    "corrupt_evidence": 409,
    "unavailable": 503,
}


class EvidenceError(Exception):
    def __init__(self, code: str, detail: str) -> None:
        if code not in STATUS:
            raise ValueError(code)
        self.code = code
        self.detail = detail
        super().__init__(detail)
