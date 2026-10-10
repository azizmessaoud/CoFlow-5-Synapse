# Row 11 report

The API exposes bounded run, event, comparison, explanation, audit, and
proposal-lineage operations. HOSTED rejects proposal mutation. LOCAL_RUNNER
stores proposals in the product boundary and creates a fresh `run_id` only
after approval. Neither profile exposes signal actuation.

Validation covers idempotency, typed HTTP 200 abstentions, explicit malformed
and over-limit errors, profile behavior, and proposal-to-run lineage.
