# Recorded comparison and limits

The five clips follow Workflow `keynote-9cce44f7`, Run `1c41e5a8-ae04-4d00-8290-861ebcbbf9b1`, domain `incident-demo`, through completion event 201. Model/tool results were recorded before the Worker stop at the approval wait.

[comparison.json](recorded/comparison.json) describes this exact Run against two newly measured uncheckpointed Python executions. The first Python process reached the same approval point and was killed. Its replacement reran the investigation because it did not restore an execution checkpoint. Input/report stores and the consumed external 429 persisted as ordinary tool side effects. The duplicate injection repeats on restart because its flag was in process memory.

[measurement_helpers.py](comparison/measurement_helpers.py) controlled the raw child processes. [raw_runner.py](comparison/raw_runner.py) uses the same prompts, evidence and explicit review protocol as the recorded Cadence case. The evidence collector retained request/response bodies and provider-reported input/output usage. Exact request equality was checked across the Cadence Run, the first raw execution and its restart. No token multiplier was assigned to a scripted planner.

For these saved receipts, each investigation received nine responses and reported 3,901 input plus 751 output tokens. The raw process did the investigation twice, so its totals are 18 responses and 9,304 tokens. The Cadence Run retained its nine recorded responses and 4,652 tokens. Stopped, replacement and final receipts show unchanged Cadence usage. The reduction is `(9304 - 4652) / 9304 = 0.5`.

This is one controlled interruption at an approval wait. It does not measure crashes halfway through model inference, guarantee exactly-once Activities, prove every agent saves half its tokens, or compare Cadence with every possible Python checkpointing design. Logical tokens include reported cached prompt tokens and are not a monetary bill. No external API fee was charged; local compute was not priced.

The copied lookup was deliberate fault injection and the review/approval inputs were automation. Presentation gates and heartbeat-protected pending log Activities controlled capture pacing. They do not establish production latency. The raw and durable paths have bounded retry and loop behavior; neither is evidence of a model spontaneously looping forever.

The first revision's higher confidence arrived without new logs. The later tool evidence supports a failure chain through payments and ledger, while the final trigger stays unknown. The frozen final response is preserved even where its wording is stronger than the evidence warrants. Human review, correctness and Workflow completion remain different concerns.

Source and raw receipt hashes are listed in [source-manifest.json](source-manifest.json). The portable wrappers change local paths, dependency loading and branding, not the frozen runtime modules. This export was checked offline. Fresh inference, recording, disconnected operation and browser playback were not rerun.

The frozen Activity adapter lists HTTP 400, 401 and 404 as nonretryable; it does not classify 403 that way. The recorded scenario exercised 429, not 403. The accompanying reusable-recipe correction adds 403 to match the presentation guidance about access errors without rewriting this historical source.
