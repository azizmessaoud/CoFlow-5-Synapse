from pathlib import Path

from coflow5.evidence.j0_ablation_capture import capture_j0_ablation_runs

if __name__ == "__main__":
    capture_j0_ablation_runs(Path(__file__).resolve().parents[1])
