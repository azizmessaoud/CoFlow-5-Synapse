# AGENT_GUIDE.md — CoFlow-5 Synapse router

Read this first. It is a router, not a manual. Put knowledge in `docs/` and specs in `.kiro/specs/`.

**Job:** build a Reliable AI decision platform on Eclipse SUMO. Five domain agents cooperate. Only A1 writes signals. Synapse explains and never actuates. Reinforcement learning is optional.

**Product vs harness:** SUMO control, agents, evidence bundle, API, and UI are the product. Router, specs, queue, evidence packs, gates, prompts, and self-tests are the harness.

Pattern source: [flyrank-bih/harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook). Output style: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT). Shopify files are not copied. The loop, evidence pack, and exit rules are lifted.

**Precedence on conflict**

1. `docs/adr/` and `docs/source/course-brief.md`
2. `.kiro/specs/coflow5-reliable-agentic-platform/`
3. `docs/harness/`
4. older narrative docs (`CoFlow-5_System_Requirements_Book.md`, `coflow5-project-context.md`)

If older text puts an LLM in the Control plane or makes DQN required, ADR-0001 wins.

## Read before any work

1. `docs/source/course-brief.md`
2. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
3. `docs/adr/0001-reliable-ai-platform-boundary.md`
4. `docs/adr/0003-cicd-devops-mlops.md` when the task is CI/CD or hosting (not a substitute for row 01)
5. `docs/harness/how-it-works.md`
6. `docs/harness/loop-and-exit.md`
7. `docs/harness/contract-and-evidence.md`
8. `.kiro/steering/product.md`
9. `CONTEXT.md`

## Read on demand

| Task | Read |
|---|---|
| Enhance specs | `.kiro/prompts/enhance-specs-trajectory.md` |
| Empathize | `coflow5-empathize-pack.md` |
| Define / Ideate | `coflow5-define-ideate.md` |
| Requirements | `.kiro/specs/coflow5-reliable-agentic-platform/requirements.md` |
| Design | `.kiro/specs/coflow5-reliable-agentic-platform/design.md` |
| Prototype/Test tasks | `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md` |
| Stack / portfolio | `docs/architecture/coflow5-synapse-portfolio-design.md` |
| SUMO / TraCI | official Eclipse SUMO docs first, not the RoadwayVR tutorial as a dependency |
| How to run SUMO | `docs/how-to-run-sumo.md` |
| Output style | `.kiro/steering/output-style.md` |

## Workflow

Unit of work = **one sealed queue row** in `harness/queue.tsv`.

1. **Plan / CAPTURE** — freeze the contract for that row. No product code unless the contract says the smoke test is the work.
2. **Build** — one worker, one row, fresh context.
3. **Converge** — fix until the machine gate is green.
4. **Gate** — `harness/work/<id>/gate.json` must pass and hash-bind the contract.
5. **Verify** — professor demo or evaluation cell as named in the contract.
6. **Follow-up** — later change requests reuse the same contract and gate.
7. **Retro** — append `LEARNINGS.md`, then promote durable rules into `docs/`.

Phases for a control row: `BUILD → CONVERGE → GATE → VERIFY`.  
Phases for a spec row: `CAPTURE → CONTRADICT → PATCH → GATE`.

## Non-negotiables

1. One signal writer: A1 only.
2. Synapse cannot reach TraCI.
3. Required recovery: Max-Pressure → actuated → fixed-time.
4. DQN is optional and cannot block the queue.
5. Truth lives in files: contract, evidence bundle, gate.json. Chat memory is not evidence.
6. A worker may not mark done by self-assessment.
7. Stop on blocked, stuck, budget, or context blow-up. See `docs/harness/loop-and-exit.md`.
8. Native Windows SUMO smoke test before Docker/WSL as a requirement.
9. Claim flags stay: no lives saved, no measured air quality, no best-episode headline.
10. Output follows `.kiro/steering/output-style.md`: next action first, numbered steps, one next step, no preamble.
