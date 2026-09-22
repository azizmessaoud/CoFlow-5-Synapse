# 02: Six-person delivery ADR

**What to build:** A short ADR-0002 records the six named builders, three pairs, one sealed queue row, course success as rows 01–09, and cuts 15→10. ADR-0001 stays accepted. Extra people do not authorize skipping the Control plane or starting Synapse before Max-Pressure.

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] ADR-0002 exists and is accepted.
- [x] ADR-0001 body is not rewritten; its three-contributor sizing is not silently overwritten.
- [x] The six names match ticket 01.
- [x] One sealed queue row is the only active unit of work.
- [x] Rows 01–09 are uncuttable; optional DQN remains blocked at row 15.
- [x] Changing one-writer, non-actuating Synapse, or required Max-Pressure still requires a new ADR, not a workshop vote.

## Answer

Accepted ADR-0002: six named builders, three pairs, one sealed row, success = 01–09. ADR-0001 unchanged.
