import zipfile

from scripts.prepare_tunis_showcase import prepare


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
