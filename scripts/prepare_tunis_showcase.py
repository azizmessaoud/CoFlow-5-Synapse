from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

REQUIRED_GTFS_FILES = {"agency.txt", "routes.txt", "stops.txt", "trips.txt", "stop_times.txt"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def prepare(
    osm_path: Path,
    gtfs_path: Path,
    output_path: Path,
    *,
    junctions_path: Path | None = None,
) -> dict[str, object]:
    if not osm_path.is_file():
        raise FileNotFoundError(f"OSM extract not found: {osm_path}")
    if not gtfs_path.is_file():
        raise FileNotFoundError(f"TRANSTU GTFS archive not found: {gtfs_path}")
    if junctions_path is not None and not junctions_path.is_file():
        raise FileNotFoundError(f"junction selection not found: {junctions_path}")
    with zipfile.ZipFile(gtfs_path) as archive:
        names = {Path(name).name for name in archive.namelist()}
    missing = sorted(REQUIRED_GTFS_FILES - names)
    if missing:
        raise ValueError("GTFS archive is missing: " + ", ".join(missing))
    manifest = {
        "status": "showcase_only",
        "sources": {
            "osm": {
                "path": str(osm_path),
                "sha256": sha256(osm_path),
                "identity": (
                    "Geofabrik Tunisia daily OSM PBF, renamed locally; "
                    "source is a whole-country extract"
                ),
                "source_url": "https://download.geofabrik.de/africa/tunisia.html",
            },
            "transtu_gtfs": {
                "path": str(gtfs_path),
                "sha256": sha256(gtfs_path),
                "identity": "official TRANSTU scheduled GTFS; verify retrieval metadata",
            },
            "aoi": (
                json.loads(junctions_path.read_text(encoding="utf-8"))
                if junctions_path is not None
                else None
            ),
        },
        "road_demand": "synthetic_or_calibrated_unless_observed_source_is_attached",
        "scheduled_transit_is_not_road_outcome_evidence": True,
        "claim_boundary": [
            "not matched-seed inference",
            "not deployment validation",
            "not measured air quality",
            "no lives saved",
            "scheduled TRANSTU data is not road-outcome evidence",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", type=Path, required=True)
    parser.add_argument("--gtfs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--junctions", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(args.osm, args.gtfs, args.output, junctions_path=args.junctions),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
