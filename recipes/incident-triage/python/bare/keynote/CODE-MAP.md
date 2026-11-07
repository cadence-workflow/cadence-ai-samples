# Code map

Use this map to separate **scripted demo setup**, **application policy**, and **Cadence platform behavior**. The frozen `source/` tree is hash-pinned; do not treat capture-only branches as product defaults.

For teaching order and clip seek times, use [PLAYBACK.md](PLAYBACK.md) and [checkpoints.json](checkpoints.json). Explain the whole agent before individual failures.

## Attribution legend

| Label | Meaning |
| --- | --- |
| Scripted | Capture harness or fixture chose the outcome before or outside normal product use |
| Application | Recipe/Workflow/Activity code policy (still not "Cadence invented this") |
| Cadence | Durable execution, scheduling, replay, Signal delivery, or history recording |

| Question | Start here | Attribution | Boundary |
| --- | --- | --- | --- |
| What does the model choose? | [plan and revise prompts](source/live_model.py) | Model (real local inference) | Inference runs inside Activities. Output validation is application code. |
| What do the tools return? | [Activities](source/activities.py), [fixtures](source/fixtures/) | Scripted fixtures | Synthetic reads and a real local SQLite keyed write. |
| Why does the gateway return 429 once? | `faults.json` written in [run_capture.py](run_capture.py); `take_fault` in [activities.py](source/activities.py) | Scripted | Capture schedules one 429. Cadence did not invent the fault. |
| What retries the 429? | `QUICK_ACTIVITY` / `SCAN_ACTIVITY` retry policy in [workflow.py](source/workflow.py) | Application policy + Cadence scheduling | Workflow declares the policy; Cadence schedules the next attempt after the raised failure. It does not reinterpret model text. |
| What prevents a repeated lookup? | `run_agent` guard in [workflow.py](source/workflow.py) | Application | Guard compares tool name and sorted arguments. Cadence preserves the recorded state that guard reads. |
| Where is the duplicate injected? | `inject_duplicate` branch in [workflow.py](source/workflow.py) | Scripted (capture-only) | Copies the prior proposal after two successful lookups; records `model_generated: false`. Does not make the model emit a duplicate or run an extra tool. |
| How do presentation pauses work? | `presentation_gate` / pending log holds | Scripted pacing | Real pending Activities and heartbeats; not a latency or UX claim. |
| How does review differ from guidance? | `revise`, `add_guidance`, waits in [workflow.py](source/workflow.py) | Application | Revision uses collected evidence. Guidance starts new tool work in the same Run. |
| Who sends the recorded Signals? | scenario sequence in [record-live.cjs](record-live.cjs) | Scripted automation | Fills the reviewer role through Cadence Web. Cadence delivers the Signals. |
| How is the Worker stopped? | `terminal_kill` in [run_capture.py](run_capture.py) | Scripted | `kill -KILL` only on child PIDs the controller started. Cadence and storage keep running. |
| What resumes after the stop? | `workers('B')` in [run_capture.py](run_capture.py), [worker.py](source/worker.py) | Cadence replay + new Workers | New identities poll the same Task List. Replay restores the approval wait from history. |
| Where are requests, responses, and usage saved? | `note_spend`, `_complete` in [live_model.py](source/live_model.py) | Application evidence capture | Outside Workflow determinism. Receipts under [recorded/](recorded/). |
| What is the Python baseline? | [raw_runner.py](comparison/raw_runner.py) | Scripted comparison peer | Same prompts and review protocol; in-memory progress; no execution checkpoint. |
| Where are the exact review inputs? | [protocol.py](comparison/protocol.py) | Scripted (shared) | Identical requests in Cadence scenario and raw baseline. |

## Events shown in the presentation

| Event | What it establishes | Attribution |
| ---: | --- | --- |
| 25 | Gateway lookup schedule and retry policy | Application policy recorded by Cadence |
| 32 | Gateway starts with `attempt: 1` after the 429 | Cadence scheduling after scripted fault |
| 33 | Gateway lookup completes | Cadence + synthetic tool success |
| 71, 73 | Inventory lookup scheduled and completed | Model choice + synthetic tool |
| 80 | Decision before blocked-duplicate pause (not event 85) | Application; pause is scripted |
| 95, 101 | First `revise` Signal and model result | Scripted Signal; model Activity |
| 105 | `guidance` Signal | Scripted Signal |
| 141 | Payments logs (ledger pool exhaustion) | Synthetic fixture content |
| 180, 186 | Second `revise` and low-confidence unknown trigger | Scripted Signal; model output |
| 190 | Approval Signal | Scripted automation |
| 197 | Keyed write on replacement Worker `activities-B` | Cadence dispatch after scripted Worker kill |
| 201 | Workflow completion | Cadence execution status only; not diagnosis certification |

The saved history belongs to one local synthetic Run. Production AES figures and the production blocked-log investigation are not part of these files.
