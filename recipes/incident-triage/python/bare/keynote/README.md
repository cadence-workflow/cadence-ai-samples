# Incident Triage: the recorded keynote demo

Public source for keynote citation: [PR #162](https://github.com/cadence-workflow/cadence-ai-samples/pull/162).
Browse the same tree on the public contributor branch without signing in:
[`recipes/incident-triage/python/bare/keynote`](https://github.com/zawadzkidiana/cadence-ai-samples/tree/issue-159-keynote-source/recipes/incident-triage/python/bare/keynote).

This folder is **historical synthetic evidence** behind five presentation clips. It is not the recommended install path for Cadence agents, and it is not the attendee Incident Triage recipe. Credibility depends on keeping scripted demo setup separate from Cadence platform behavior. Read the attribution table before the narrative.

**Opening hook:** agents fail mid-investigation; Workflows can recover from recorded state.

**Explain the whole agent first:** Trace → read logs → draft report → engineer reviews → save. Then follow failed lookup, incomplete diagnosis, human guidance, and same-Run recovery. Use the [playback guide](PLAYBACK.md) and [checkpoints.json](checkpoints.json) for that order. Keep the real production observation separate from this reconstructed public demo. Show the measured work comparison before introducing Reset.

Start with [PLAYBACK.md](PLAYBACK.md), then [CODE-MAP.md](CODE-MAP.md) and [METHODOLOGY.md](METHODOLOGY.md), and inspect the [saved Run](recorded/run.json).

## Attribution: scripted setup vs Cadence behavior

Every row below is intentional. Do not treat the left column as a Cadence feature claim.

| Observation in the clips | Who caused it | What Cadence actually did |
| --- | --- | --- |
| Synthetic checkout logs, graph, and incident text | Demo fixtures and `faults.json` | Stored and replayed Workflow/Activity events for that input |
| First gateway lookup returns HTTP 429 once | Capture writes `faults.json` before start (`run_capture.py`) | Applied the Workflow's Activity retry policy (10s, max 3) and scheduled attempt 1 |
| "Duplicate" tool lookup appears and is blocked | Capture-only `inject_duplicate` copies the prior proposal; `model_generated: false` | Persisted Workflow state and the application guard decision; did not invent the duplicate |
| Ordinary repeated-call blocking (separate from injection) | Application guard on tool name + sorted arguments | Preserved the state the guard reads on replay |
| Presentation pauses / pending log Activities | Capture holds (`presentation_mode`, heartbeats) | Kept a real pending Activity and Worker lease; pacing is demo control, not latency proof |
| `revise`, `guidance`, and `approval` Signals | Recorder automation (`record-live.cjs`), not a human operator | Delivered Signals into the open Run and continued the Workflow |
| Worker processes disappear mid-approval wait | Recorder kills only PIDs it started | Cadence and DB stayed up; replacement Workers polled the same Task List; replay restored the wait with **zero** new model calls |
| Final `root_cause: unknown`, `confidence: low` | Model output on synthetic evidence, after scripted review inputs | Recorded completion; completion is not a correctness certificate |
| 9 vs 18 model responses / 4,652 vs 9,304 logical tokens | Same prompts and review protocol; raw path has no execution checkpoint | Cadence retained recorded Activity results across the Worker stop; the raw Python process re-ran the investigation |

**Cadence is not claimed to:** invent the duplicate, write the review Signals, inject the 429, choose Qwen, guarantee half tokens for every agent, or certify the diagnosis.

**This export is not:** the reusable recipe, Explorer onboarding, or "how to install agents." Those stay in the [repository README](../../../../../README.md) and [Incident Triage recipe](../../../README.md).

### External review in one command

No Cadence, Ollama, browser, paid API, or GitHub login is required to audit the frozen evidence:

```sh
git clone https://github.com/zawadzkidiana/cadence-ai-samples.git
cd cadence-ai-samples
git checkout issue-159-keynote-source
cd recipes/incident-triage/python/bare/keynote
python3 verify_recording.py
python3 verify_checkpoints.py
```

Expect `checks: PASS` from both, an `attribution` block naming scripted vs Cadence responsibilities, nine playback checkpoints, 201 events, Cadence 9 responses / 4,652 logical tokens, and the uncheckpointed baseline 18 responses / 9,304 logical tokens.

The reusable recipe's current constrained planner can follow the ERROR path directly. It is not expected to reproduce the recorded wrong turn, wording, or token counts.

## What happened (labeled)

1. **Scripted:** gateway lookup faulted once with 429 via `faults.json`. **Cadence:** retried that Activity after 10 seconds per the Workflow policy. The independent graph lookup ran once.
2. **Scripted:** after two successful agent lookups, the capture branch copied the tool proposal and marked it blocked before dispatch (`inject_duplicate`). This is not spontaneous model looping. **Separate application behavior:** the ordinary guard still checks proposed tool names and sorted arguments; a turn budget bounds the loop. **Cadence:** persisted that state.
3. **Model + scripted review:** first draft had low confidence. **Scripted:** an automated `revise` Signal requested evidence quotes. That revision became highly confident without fetching new logs.
4. **Scripted:** an automated `guidance` Signal directed investigation through payments and ledger; a second automated `revise` asked to separate observed errors from the unknown trigger. Approval remained a separate Signal.
5. **Scripted:** the recorder killed only its two Worker processes. **Cadence:** service and database stayed running; replacement Workers restored the same approval wait; no model calls repeated. **Scripted:** automation then approved; **Cadence:** the keyed write completed on the replacement Activity Worker.

The final recorded fields are `root_cause: unknown` and `confidence: low`. The logs show connection exhaustion. They do not establish what triggered it. A model-written sentence excluding inventory is not independent proof that inventory could not contribute.

## Read the evidence without running services

Python 3.12 or 3.13 is sufficient. This command uses only the standard library and makes no network calls:

```sh
python3 verify_recording.py
```

It verifies frozen-file hashes, reported usage, request equality, model completions, review Signals, the retry policy, Worker identities, injection flags (`presentation_mode`, `inject_duplicate`, `model_generated: false`), and final completion. See [the methodology](METHODOLOGY.md) for the comparison and its limits.

| Saved observation | Cadence Run | Uncheckpointed Python, including restart |
| --- | ---: | ---: |
| Model responses | 9 | 18 |
| Input tokens | 3,901 | 7,802 |
| Output tokens | 751 | 1,502 |
| Logical tokens | 4,652 | 9,304 |
| New model responses during recovery | 0 | 9 |

That is 50% fewer logical tokens in this recovery comparison. It is not a monetary savings measurement. Local inference has compute costs, and a Python design with persistent checkpoints can recover differently.

### Reset (after the comparison)

**Reset** starts a new Run under the same Workflow ID from a supported boundary. It does not undo external effects. The deck may show a Ctrl+Z visual; keep that limit explicit. Same-Run Worker recovery in the clips is not Reset.

## Credits

Thanks to Ethan Lee, Sean Po, Daniel Yao, and the Michelangelo team for the production context that motivated this teaching reconstruction. Public materials here use synthetic fixtures only.

## Set up a fresh local capture (optional, not bit-identical)

A new capture can exercise the same harness. Wording and timing can differ from
the frozen clips. On 2026-11-07 a full portable capture was rerun successfully
(Playwright + local Qwen2.5:7b + Cadence/Web): 201 events, 9 responses, matching
3,901 / 751 tokens for that run, with scripted 429, injected duplicate, and Worker
recovery. Runtime modules in `source/` are hash-pinned. Synthetic log fixtures under
`source/fixtures/logs/` are required for any fresh capture; without them the
gateway lookup fails after the scripted 429. [The manifest](source-manifest.json)
records every original/export hash and controller adaptations.

From this directory, prepare an environment with Python 3.12 or 3.13:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install
npx playwright install chromium
```

Use a local Cadence frontend on `localhost:7833`, Web on `http://localhost:8088`, and an existing local domain `incident-demo`. Domain provisioning is separate. Set `CADENCE_TARGET`, `CADENCE_WEB_URL` and `CADENCE_DOMAIN` if your local ports or domain differ.

For the repository's recommended Qwen path (not required for offline verify):

```sh
ollama pull qwen2.5:7b
```

```sh
export INCIDENT_TRIAGE_CATALOG="$(cd ../../../../../ && pwd)/models.yaml"
export INCIDENT_TRIAGE_MODEL_ID=qwen2.5-local
```

The frozen `source/models.yaml` preserves the recording's isolated `qwen-local` ID and port 11435. Both select Qwen2.5:7b. Do not confuse the historical catalog ID with the repository's recommended one. The generic recipe's live default is still Llama unless explicitly selected.

In terminal 1:

```sh
.venv/bin/python run_capture.py
```

Wait for it to print a new Workflow/Run ID, then in terminal 2:

```sh
node record-live.cjs
```

The controller creates a fresh `capture/` and refuses to overwrite one. To make another recording, set the same new `KEYNOTE_CAPTURE_DIR` in both terminals. The recorder opens a real Cadence Web session, releases presentation pauses, sends the review Signals, stops its owned demo Workers, and records browser video. Never point this fault-injection harness at a shared or production installation.

`comparison/derive_comparison.py` makes new local model calls for an uncheckpointed first execution and restart. It writes to `comparison/measured/` and refuses to reuse an existing measurement directory. New model versions, hardware, decoding, and outputs may change results; do not replace the historical counts with an assumption.

## What this export does not change

The reusable recipe, its Explorer controls, the live retry exercise (#116), timeout fix (#117), and walkthrough (#154) remain separate. The final clips also contain later editing, sound cues, and selected CLI history overlays. Those CLI excerpts were retrieved after this Run completed; they were not a continuous terminal recording beside the original browser. This folder exports runtime, recording, and measurement code, not the deck or video editing pipeline.
