# ADR-0002: Six named builders, one sealed queue row

ADR-0001 stays accepted: CoFlow-5 is a reliable AI decision platform; only A1 writes signals; cooperative Max-Pressure is required; Synapse never reaches TraCI; DQN is optional.

We now have six named ESPRIT 4DS builders, not three anonymous critical-path slots. Extra people do not authorize parallel product work, Synapse before Max-Pressure, or skipping the Control plane.

**Status:** Accepted  
**Date:** 22 September 2026

## Decision

1. The delivery team is Aziz Messaoud, Eya Laourine, Fares Ben Kacem, Mohamed Aymen Hamzaoui, Oumayma Saddouri, and Ranim Ben Salem.
2. They work as three pairs: Control (Aziz, Fares); Data/Evaluation (Aymen, Oumayma); Cooperation/Product (Eya, Ranim).
3. Only one sealed queue row is active. Course/reliability success is rows 01–09. Cuts proceed 15 → 14 → 13 → 12 → 11 → 10.
4. Row 15 optional DQN remains blocked until the cooperative core freezes.
5. Changing one-writer authority, non-actuating Synapse, or required Max-Pressure still needs a new ADR, not a workshop vote.

## Why

Six beginners can test and explain in parallel. They cannot each own a later row at once without breaking the evidence contract. ADR-0001’s three-contributor *sizing* was a schedule bound; this ADR names the six people and keeps the same bound as **one active row**.

## Considered options

- Rewrite ADR-0001 “three” to “six” and open rows 10–15 immediately — rejected; that skips the Control plane.
- Leave names only in the book — rejected; a future reader of ADR-0001 would think three people still authorize the envelope.
