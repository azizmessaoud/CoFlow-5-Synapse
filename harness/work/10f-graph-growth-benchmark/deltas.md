# Row 10f deltas

Open deltas: **0**

- Implemented the sealed four-signal graph, OD generator, immutable parser/hash, bounded scorer, fallback probes, native runner, fixture matrix, graph frames, joins, and optional watcher.
- All five sealed test commands pass.
- Native smoke remains visibly `failed` with `WinError 4551`; this is not an open contract delta because the sealed contract explicitly permits deterministic fixture evidence plus an honestly documented native smoke when Windows blocks execution.
- Rows 05 and 10b remain hash-stable; no GNN, DQN, NetworkX, React, WebSocket, hosted LLM, or RoadwayVR runtime dependency was added.
