import zipfile
import json
from pathlib import Path

from scripts import build_tunis_sumo
from scripts.prepare_tunis_showcase import prepare


def test_showcase_build_defaults_to_committed_osm_not_a_machine_local_path() -> None:
    assert build_tunis_sumo.OSM == Path(build_tunis_sumo.ROOT / "scenarios/tunis-showcase/tunis.osm.xml")
    assert build_tunis_sumo.OSM.is_file()
    assert "C:\\Users\\" not in Path(build_tunis_sumo.__file__).read_text(encoding="utf-8")


def test_committed_showcase_manifest_hashes_the_osm_snapshot() -> None:
    manifest = json.loads((build_tunis_sumo.SCENARIO / "tunis.source.json").read_text(encoding="utf-8"))
    roads = manifest["roads"]
    assert roads["imported_osm_xml_sha256"] == build_tunis_sumo.sha256(build_tunis_sumo.OSM)
    assert roads["source_url"].startswith("https://download.geofabrik.de/")
    assert roads["license"] == "Open Database License (ODbL)"
    selection = json.loads((build_tunis_sumo.ROOT / "scenarios/tunis-centre-6j/selection.json").read_text(encoding="utf-8"))
    assert roads["original_pbf_sha256"] == selection["aoi"]["source"]["sha256"]
    assert roads["original_pbf_data_as_of_utc"] == "2026-10-15T20:21:00Z"


def test_tunis_manifest_labels_synthetic_road_demand(tmp_path) -> None:
    osm = tmp_path / "tunis.osm.xml"
    osm.write_text("<osm version='0.6' />", encoding="utf-8")
    gtfs = tmp_path / "transtu.zip"
    with zipfile.ZipFile(gtfs, "w") as archive:
        for name in (
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        ):
            archive.writestr(name, "id\n1\n")

    manifest = prepare(
        osm,
        gtfs,
        tmp_path / "manifest.json",
        gtfs_url="https://example.test/transtu.zip",
        gtfs_retrieved_at="2026-10-10",
    )

    assert manifest["status"] == "showcase_only"
    assert manifest["road_demand"].startswith("synthetic")
    assert manifest["scheduled_transit_is_not_road_outcome_evidence"] is True
    assert "no lives saved" in manifest["claim_boundary"]
    assert manifest["sources"]["transtu_gtfs"]["source_url"].startswith("https://")
    assert manifest["sources"]["transtu_gtfs"]["publisher_verified"] is False
    assert "not independently verified" in manifest["sources"]["transtu_gtfs"]["identity"]
