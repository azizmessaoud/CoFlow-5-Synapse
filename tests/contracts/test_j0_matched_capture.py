import pytest

from coflow5.evidence.j0_matched_capture import DEFAULT_SEEDS, capture_j0_matched_runs


def test_j0_capture_rejects_fewer_than_five_declared_seeds(tmp_path) -> None:
    with pytest.raises(ValueError, match="at least five"):
        capture_j0_matched_runs(tmp_path, seeds=DEFAULT_SEEDS[:4])
