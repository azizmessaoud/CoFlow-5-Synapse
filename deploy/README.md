# Later read-only deploy

This folder is the **product CD shape** from [ADR-0003](../docs/adr/0003-cicd-devops-mlops.md). It is not the native Windows smoke test.

Images:

1. `api` — FastAPI reads `EVIDENCE_ROOT`. It does not launch a simulator and does not actuate signals.
2. `ui` — React build served by nginx. Proxies `/api/` to the API.

Neither image installs a traffic simulator. Rollback is the previous git tag plus the previous tagged evidence directory.

```powershell
cd deploy
docker compose up --build
```

Open `http://localhost:8080`. Health: `http://localhost:8000/health`.

Row 01 now has a passing `gate.json`, so this compose file is the allowed later product path. It still does not deploy into a city, and neither image contains a simulator. Replace `deploy/evidence/demo-readonly-0001/` with a tagged evidence bundle before calling the hosted page a real run. The fixture stays labelled `status: fixture`.

Do not use this compose as the row 01 command. Native smoke remains `py -3.11 scripts\run_native_smoke.py` on Windows.
