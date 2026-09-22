from pathlib import Path

from coflow5.evidence.cooperation_artifacts import generate_cooperation_artifacts


if __name__ == "__main__":
    generate_cooperation_artifacts(Path(__file__).resolve().parents[1])
