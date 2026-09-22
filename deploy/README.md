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

Replace `deploy/evidence/demo-readonly-0001/` with a real bundle (`run_id`, `scenario_hash`, Parquet/KPI files) after rows 02 and 09 gate. The demo fixture is labelled `status: fixture` on purpose.

Do not use this compose as the row 01 command. Native smoke remains `py -3.11 scripts\run_native_smoke.py` on Windows.
