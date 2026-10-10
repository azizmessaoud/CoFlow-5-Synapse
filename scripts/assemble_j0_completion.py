from pathlib import Path

from coflow5.evidence.j0_completion_bundle import assemble_j0_completion_bundle


if __name__ == "__main__":
    bundle = assemble_j0_completion_bundle(Path(__file__).resolve().parents[1])
    print(f"status={bundle['status']} findings={len(bundle['audit']['findings'])}")
