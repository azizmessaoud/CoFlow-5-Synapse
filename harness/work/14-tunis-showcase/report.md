# Tunis showcase status

The local PBF input is present and hash-verified in `pbf-source.json`. The
ingestion seam is implemented in `scripts/prepare_tunis_showcase.py`, and the
six-junction extractor is implemented in `scripts/find_tunis_junctions.py`.
The extractor ran successfully in WSL Ubuntu and produced six deterministic
junctions with OSM node IDs, coordinates, degree, scores, tags, and way
references. The row remains blocked only until an official TRANSTU GTFS ZIP
and retrieval metadata are supplied. No Tunis result is presented as measured
evidence.
