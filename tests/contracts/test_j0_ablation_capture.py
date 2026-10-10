from pathlib import Path

import pytest

from coflow5.evidence.j0_ablation_capture import capture_j0_ablation_runs


def test_ablation_capture_requires_five_seeds(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least five seeds"):
        capture_j0_ablation_runs(tmp_path, seeds=(37,))
