"""Fail honestly when this runner cannot import libsumo (ADR-0003)."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import libsumo
    except Exception as exc:  # noqa: BLE001 — any import failure is Exit 3
        print(
            "eval.yml Exit 3: this runner cannot import libsumo. "
            "Use a self-hosted Windows runner with pinned SUMO 1.27.1 "
            "and an allowed libsumo. Do not treat a missing SUMO as a pass. "
            f"Cause: {type(exc).__name__}: {exc}"
        )
        return 1
    print("libsumo", libsumo.__file__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
