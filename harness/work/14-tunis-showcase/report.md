# Tunis showcase status

The local PBF input is present and hash-verified in `pbf-source.json`. The
ingestion seam is implemented in `scripts/prepare_tunis_showcase.py`, and the
six-junction extractor is implemented in `scripts/find_tunis_junctions.py`.
The local run was blocked because Windows application-control policy prevents
the pyosmium native DLL from loading. The row also remains blocked until an
official TRANSTU GTFS ZIP and retrieval metadata are supplied. No Tunis result
is presented as measured evidence.
