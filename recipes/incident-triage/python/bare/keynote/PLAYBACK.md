# Playback guide: understand the agent, then the failures

This guide is for people replaying the recorded experiment or teaching from the
five clips. It is concise teaching guidance, not a finished speaker script.

Public source: [PR #162](https://github.com/cadence-workflow/cadence-ai-samples/pull/162).
Frozen Run: Workflow `keynote-9cce44f7`, Run `1c41e5a8-ae04-4d00-8290-861ebcbbf9b1`.
Machine-readable checkpoints: [checkpoints.json](checkpoints.json).

Keep the opening hook: agents fail mid-investigation; Workflows can recover from
recorded state. Then explain the whole agent before individual failures.

## Explain the whole agent first

Map the path once before zooming into errors:

**Trace → read logs → draft report → engineer reviews → save**

Cumulative step history used in playback: **Trace, Graph, Logs, Draft, Review, Save**.
Highlight the current step. Distinguish completed work from waiting. Show one
readable evidence item at a time. Label confidence as model-reported (pair color
with text; red for low). Keep the new-lookup count visible during revision.

## Production observation vs public demo

Keep these separate.

| | Production observation | Public demo in this folder |
| --- | --- | --- |
| What happened | On-call run: seven log-access calls were denied; nobody authorized access | Synthetic checkout incident with fixtures and local Qwen2.5:7b |
| Retries | Those seven denials were **not** seven Cadence Activity retries | One injected gateway HTTP 429; Cadence scheduled the Activity retry |
| Outcome | Harness returned normally inside its Activity; Workflow finished its code path without a diagnosis | Investigation continues with review Signals, guidance, and approval |
| Gap | A structured wait for human review was missing | Demo adds explicit revise, guidance, and approval waits |
| Continuity | We do **not** resume the production execution | We reconstruct narratively with a new synthetic Run |

## Watching a recording vs reproducing the experiment

| Goal | What to do |
| --- | --- |
| Audit frozen evidence offline | `python3 verify_recording.py` then open [PLAYBACK checkpoints](checkpoints.json) |
| Watch the edited clips | Use slide 18, 21, 24, 27, 30 clips. Seek times below are verified against those MP4s (2026-11-07). Reading holds are editorial, not measured retry delays. |
| Reproduce a fresh capture | Follow [README setup](README.md#set-up-a-fresh-local-capture-optional-not-bit-identical). Requires Cadence, Web, Ollama, Playwright. Results can differ. |

Clip files (not stored in git; cited from the deck build):

| Slide | Clip | Duration |
| ---: | --- | ---: |
| 18 | `01-temporary-error-retry.mp4` | 28.32s |
| 21 | `02-repeated-lookup-prevention.mp4` | 43.24s |
| 24 | `03-review-existing-evidence.mp4` | 18.08s |
| 27 | `04-guidance-and-new-evidence.mp4` | 74.72s |
| 30 | `05-worker-stop-and-recovery.mp4` | 57.08s |

## Checkpoints

Each checkpoint answers: what already ran, what to notice, what changed, what
Cadence preserved, what to do next. Teaching prompts are questions, not lines to
read verbatim.

### 1. `setup-and-agent-map` — Customer impact and setup

- **Already executed:** nothing yet (or only Workflow start).
- **Notice:** checkout fails with HTTP 500; service map; synthetic scope.
- **Prompt:** What should survive if a Worker disappears mid-investigation?
- **Next:** State the agent map, then open clip 18 or the offline verifier.
- **Recording:** narrative before clip 01 (no seek inside an edited MP4).

### 2. `lookup-fails-then-recovers` — Lookup fails, then recovers

- **Already executed:** Trace, Graph (graph saved once).
- **Waiting:** Logs (gateway).
- **Notice:** injected HTTP 429 on the gateway lookup; retry policy 10s / max 3;
  Cadence starts attempt 1. Keep the error readable before recovery.
- **Prompt:** Which work needs another attempt, and which result is already saved?
- **Cadence preserved:** the completed graph result; schedules the failed lookup retry.
- **Next:** Watch through recovery or release the capture hold.
- **Recording:** slide 18, seek **5.3s** (`gateway-retry-started`). Events 25, 32.

### 3. `read-returned-evidence` — Read the returned evidence

- **Already executed:** Trace, Graph, Logs.
- **Notice:** gateway ERROR `upstream returned 503`. This incident error is
  separate from the lookup request's 429.
- **Prompt:** What does the 503 tell the agent to inspect next?
- **Next:** Follow model tool choices into checkout / inventory.
- **Recording:** slide 18, seek **13.6s** (`gateway-completed`). Event 33.

### 4. `copied-lookup-blocked` — Copied lookup is blocked

- **Already executed:** Trace, Graph, Logs (including inventory).
- **Notice:** `injected_proposal` with `model_generated: false`, `executed: false`.
  Application code blocked a deliberately copied inventory proposal.
- **Prompt:** What should product code own versus what the platform records?
- **Cadence preserved:** Workflow state used by the guard; it did not invent the duplicate.
- **Next:** Continue to the first draft.
- **Recording:** slide 21, seek **23.2s** (`duplicate-blocked`). Events 71, 73, 80.

### 5. `first-diagnosis-incomplete` — First diagnosis is incomplete

- **Already executed:** Trace, Graph, Logs, Draft.
- **Notice:** draft blames inventory with **low** confidence; payments/ledger
  evidence missing. Confidence is model-reported.
- **Prompt:** Would you approve this draft with the evidence on screen?
- **Next:** Revise using existing ERROR quotes only (no new lookup yet).
- **Recording:** slide 21, seek **31.5s** (`model-9-model_response`). Event 87.

### 6. `confidence-not-new-evidence` — Confidence is not new evidence

- **Already executed:** Trace, Graph, Logs, Draft, Review (first revise).
- **Notice:** confidence becomes **high**; **new log lookups: 0**.
- **Prompt:** What would you require before trusting a confidence jump?
- **What changed:** wording and reported confidence, not the evidence set.
- **Next:** Guidance toward payments and ledger.
- **Recording:** slide 24, seek **9.75s** (`first-revision`). Events 95, 101.

### 7. `human-guidance-changes-path` — Human guidance changes the investigation

- **Already executed:** prior steps; Review continues with new tool work.
- **Notice:** after guidance, payments/ledger logs show connection-pool
  exhaustion; final reviewed report keeps `root_cause: unknown`, confidence low.
- **Prompt:** What evidence appeared after guidance that the first draft lacked?
- **What changed:** new lookups in the **same Run**; trigger still unknown.
- **Cadence preserved:** earlier Activity results; continues the same execution.
- **Next:** Reach approval wait. Finish the measured comparison before Reset.
- **Recording:** slide 27, seek **0.0s** (`signal-guidance`). Events 105, 141, 180, 186.

### 8. `workers-stop-at-approval` — Workers stop at the approval wait

- **Already executed:** Trace, Graph, Logs, Draft, Review.
- **Waiting:** Save (approval).
- **Notice:** both demo Workers stop; Cadence service and database remain running.
  Make that failure boundary explicit.
- **Prompt:** What must still be true for a replacement Worker to continue without re-calling the model?
- **Cadence preserved:** open Run, history, recorded model/tool results, usage unchanged at stop.
- **Next:** Start replacement Workers on the same Task List.
- **Recording:** slide 30, seek **8.95s** (`workers-stopped`).

### 9. `same-run-recovery` — Replacement Workers finish the same Run

- **Already executed:** full path through Save.
- **Notice:** same Workflow ID and Run ID before and after; approval; write on
  `activities-B`; **0** new model calls during recovery.
- **Prompt:** How does this differ from starting a new Run?
- **Cadence preserved:** replay restores the approval wait from history.
- **Next:** Show the measured comparison table. Only then introduce Reset.
- **Recording:** slide 30, seek **20.62s** (`workers-restored`). Events 190, 197, 201.

## Measured work comparison (before Reset)

Show this immediately after same-Run recovery. Do not convert tokens into dollars.

| Measured work | Python restart | Cadence same-Run recovery |
| --- | ---: | ---: |
| Model responses | 18 | 9 |
| Input tokens | 7,802 | 3,901 |
| Output tokens | 1,502 | 751 |
| Total logical tokens | 9,304 | 4,652 |
| Additional model calls after interruption | 9 | 0 |

One controlled comparison: local Qwen2.5:7b, interrupted at approval wait. No
external model API charge; compute and infrastructure unpriced. Details:
[METHODOLOGY.md](METHODOLOGY.md), [recorded/comparison.json](recorded/comparison.json).

## Reset (separate, after the comparison)

**Reset** starts a **new Run** under the same Workflow ID from a supported
boundary. It does not undo external effects. The deck may use a Ctrl+Z visual;
keep that limit explicit. Reset is not what happened in checkpoint
`same-run-recovery`.

## Credits

Thanks to Ethan Lee, Sean Po, Daniel Yao, and the Michelangelo team for the
production context that motivated this teaching reconstruction. Public materials
in this folder use synthetic fixtures only.

## Related files

- [README.md](README.md) — attribution, offline verify, fresh capture
- [CODE-MAP.md](CODE-MAP.md) — code boundaries
- [METHODOLOGY.md](METHODOLOGY.md) — comparison limits
- [verify_recording.py](verify_recording.py) — offline PASS + attribution
- [verify_checkpoints.py](verify_checkpoints.py) — checkpoint event references
