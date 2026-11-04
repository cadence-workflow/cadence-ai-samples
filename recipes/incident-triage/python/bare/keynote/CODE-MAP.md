# Code map

| Question | Start here | Boundary |
| --- | --- | --- |
| What does the model choose? | [plan and revise prompts](source/live_model.py) | Real local inference inside Activities. Output validation is application code. |
| What do the tools return? | [Activities](source/activities.py), [fixtures](source/fixtures/) | Synthetic reads and a real local SQLite keyed write. |
| What retries the 429? | `QUICK_ACTIVITY` and `SCAN_ACTIVITY` in [workflow.py](source/workflow.py) | Workflow code declares a policy; Cadence schedules Activity attempts after a raised failure. It does not reinterpret model text. |
| What prevents a repeated lookup? | `run_agent` in [workflow.py](source/workflow.py) | Application guard compares the tool and sorted arguments. Cadence preserves the recorded state used by that guard. |
| Where is the duplicate injected? | `inject_duplicate` branch in [workflow.py](source/workflow.py) | Capture-only copied proposal after two successful agent lookups. It records a blocked proposal directly; it does not make the model generate a duplicate or run an extra tool. |
| How does review differ from guidance? | `revise`, `add_guidance`, and the waits in [workflow.py](source/workflow.py) | Revision uses already collected evidence. Guidance starts new tool investigation in the same Run. Past review requests are not silently reapplied after guidance. |
| Who sends the recorded Signals? | `signal` and scenario sequence in [record-live.cjs](record-live.cjs) | Recorder automation fills the reviewer role through Cadence Web. |
| How is the Worker stopped? | `terminal_kill` in [run_capture.py](run_capture.py) | Sends `kill -KILL` to only the child PIDs it started, then checks them with `ps`. It leaves Cadence and storage running. |
| What resumes after the stop? | `workers('B')` in [run_capture.py](run_capture.py), [worker.py](source/worker.py) | New Worker identities poll the same Task List. Workflow replay restores the approval wait from recorded events. |
| Where are requests, responses and usage saved? | `note_spend`, `_complete` in [live_model.py](source/live_model.py) | Local evidence capture, outside Workflow code. Raw and Cadence receipts are under [recorded/](recorded/). |
| What is the Python baseline? | [raw_runner.py](comparison/raw_runner.py) | Bounded retries, loop guard, in-memory progress and persistent tool side effects, without an execution checkpoint. |
| Where are the exact review inputs? | [protocol.py](comparison/protocol.py) | The same requests are used in the recorded Cadence scenario and raw baseline. |

## Events shown in the presentation

| Event | What it establishes |
| ---: | --- |
| 25 | Gateway lookup schedule and retry policy. |
| 32 | Gateway starts with `attempt: 1`, the second attempt, after the 429. |
| 33 | Gateway lookup completes. |
| 71, 73 | Inventory lookup is scheduled and completed. |
| 80 | Decision completion before the blocked-duplicate presentation pause. Do not use event 85 for that earlier moment. |
| 95, 101 | First `revise` Signal and its model result. |
| 105 | `guidance` Signal. |
| 141 | Payments logs, including the ledger pool exhaustion and timeout. |
| 180, 186 | Second explicit `revise` Signal and the report with low confidence and unknown trigger. |
| 190 | Approval Signal sent by automation. |
| 197 | The keyed report write commits on replacement Worker `activities-B`. |
| 201 | Workflow completion. Completion records execution status; it does not certify the diagnosis. |

The saved history belongs to one local synthetic Run. Production AES figures and the production blocked-log investigation are not part of these files.
