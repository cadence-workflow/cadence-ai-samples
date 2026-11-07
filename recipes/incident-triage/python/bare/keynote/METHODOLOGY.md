# Recorded comparison and limits

The five clips follow Workflow `keynote-9cce44f7`, Run `1c41e5a8-ae04-4d00-8290-861ebcbbf9b1`, domain `incident-demo`, through completion event 201. Model and tool results were recorded before the Worker stop at the approval wait.

This document states what was measured and what was deliberately arranged. It does not treat scripted faults as emergent Cadence behavior.

## What was arranged (scripted)

- Synthetic incident text, logs, graph, and SQLite-backed write fixtures.
- One gateway HTTP 429 via capture `faults.json` before Workflow start.
- Capture-only `inject_duplicate` after two successful lookups (`model_generated: false`).
- Presentation gates and heartbeat-protected pending log Activities for pacing.
- Automated `revise`, `guidance`, and `approval` Signals from the recorder.
- Controlled kill of only the capture-owned Worker processes.
- Identical review protocol strings for the Cadence Run and the raw Python baseline ([protocol.py](comparison/protocol.py)).

## What Cadence did in this Run

- Recorded Workflow and Activity history for the synthetic input.
- Applied the Workflow-declared Activity retry policy after the raised 429.
- Delivered Signals into the open Run.
- Kept the service and database up while demo Workers were killed.
- Allowed replacement Workers to resume from recorded history at the approval wait with no new model calls.
- Completed the keyed write on the replacement Activity Worker identity.

## Comparison method

[comparison.json](recorded/comparison.json) describes this exact Run against two newly measured uncheckpointed Python executions. The first Python process reached the same approval point and was killed. Its replacement reran the investigation because it did not restore an execution checkpoint. Input/report stores and the consumed external 429 persisted as ordinary tool side effects. The duplicate injection repeats on restart because its flag was in process memory.

[measurement_helpers.py](comparison/measurement_helpers.py) controlled the raw child processes. [raw_runner.py](comparison/raw_runner.py) uses the same prompts, evidence, and explicit review protocol as the recorded Cadence case. The evidence collector retained request/response bodies and provider-reported input/output usage. Exact request equality was checked across the Cadence Run, the first raw execution, and its restart. No token multiplier was assigned to a scripted planner.

For these saved receipts, each investigation received nine responses and reported 3,901 input plus 751 output tokens. The raw process did the investigation twice, so its totals are 18 responses and 9,304 tokens. The Cadence Run retained its nine recorded responses and 4,652 tokens. Stopped, replacement, and final receipts show unchanged Cadence usage. The reduction is `(9304 - 4652) / 9304 = 0.5`.

Present this measured comparison immediately after same-Run recovery in teaching order. Introduce **Reset** only afterward: Reset starts a new Run under the same Workflow ID from a supported boundary and does not undo external effects. Same-Run Worker recovery in this experiment is not Reset.

## Explicit non-claims

This is one controlled interruption at an approval wait. It does not:

- measure crashes halfway through model inference;
- guarantee exactly-once Activities;
- prove every agent saves half its tokens;
- compare Cadence with every possible Python checkpointing design;
- treat the injected duplicate as model or Cadence misbehavior;
- treat automated review Signals as human operator judgment;
- treat presentation pacing as production latency;
- treat Workflow completion as diagnosis correctness.

Logical tokens include reported cached prompt tokens and are not a monetary bill. No external API fee was charged; local compute was not priced.

The first revision's higher confidence arrived without new logs. The later tool evidence supports a failure chain through payments and ledger, while the final trigger stays unknown. The frozen final response is preserved even where its wording is stronger than the evidence warrants. Human review, correctness, and Workflow completion remain different concerns.

Source and raw receipt hashes are listed in [source-manifest.json](source-manifest.json). The portable wrappers change local paths, dependency loading, and branding, not the frozen runtime modules. The frozen export is checked offline by `verify_recording.py`. On 2026-11-07 a fresh portable capture was also rerun successfully against local Cadence (`localhost:27833`), Cadence Web (`http://127.0.0.1:28089`), domain `incident-demo`, Playwright, and Ollama `qwen2.5:7b` (Workflow `keynote-d24db5df`, Run `b8c8e843-d10a-4934-bbb0-2e59190de278`): 201 history events, 9 model responses, 3,901 / 751 tokens, scripted 429 + injected duplicate + Worker stop/restart with unchanged usage across the stop, and `service_completed: true`. That rerun required restoring `source/fixtures/logs/`, which had been missing from the export. Fresh captures can still differ in wording and timing; do not treat token equality as guaranteed.

The frozen Activity adapter lists HTTP 400, 401, and 404 as nonretryable; it does not classify 403 that way. The recorded scenario exercised 429, not 403. The accompanying reusable-recipe correction adds 403 to match the presentation guidance about access errors without rewriting this historical source.
