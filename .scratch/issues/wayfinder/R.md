---
name: r-deploy
description: Deployment package, tagged bundles, and CI
labels: [wayfinder:task]
parent: wayfinder-map
blocking: [13]
---

## Question
How do we package the system into a reproducible Docker Compose deploy that serves a tagged evidence bundle?

**Required Actions:**
- Create `scripts/seal_bundle.py` for SHA256 tagging.
- Implement `release.yml` for image building and smoke tests.
- Write `docs/demo/script.md`.
- Verify `docker compose up` serves the tagged real bundle.
