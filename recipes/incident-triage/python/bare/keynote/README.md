# Incident Triage: the recorded keynote demo

Public source for keynote citation: [PR #162](https://github.com/cadence-workflow/cadence-ai-samples/pull/162).
Browse the same tree on the public contributor branch without signing in:
[`recipes/incident-triage/python/bare/keynote`](https://github.com/zawadzkidiana/cadence-ai-samples/tree/issue-159-keynote-source/recipes/incident-triage/python/bare/keynote).

Start with [the code map](CODE-MAP.md) and [methodology](METHODOLOGY.md), then inspect the [saved Run](recorded/run.json).
This is the source behind the five keynote clips. The experiment path is synthetic checkout logs into a local Qwen2.5:7b model, with injected failures and automated review Signals. The production case in the presentation is separate and is not included here.

### External review in one command

No Cadence, Ollama, browser, paid API, or GitHub login is required to audit the frozen evidence:

```sh
git clone https://github.com/zawadzkidiana/cadence-ai-samples.git
cd cadence-ai-samples
git checkout issue-159-keynote-source
cd recipes/incident-triage/python/bare/keynote
python3 verify_recording.py
```

Expect `checks: PASS`, 201 events, Cadence 9 responses / 4,652 logical tokens, and the uncheckpointed baseline 18 responses / 9,304 logical tokens.

The reusable [Incident Triage recipe](../../../README.md) remains the attendee starting point. Its current constrained planner can follow the ERROR path directly. It is not expected to reproduce the recorded wrong turn, wording or token counts. This folder preserves the earlier presentation runtime so the recording can be audited without weakening that recipe.

## What happened

1. A gateway log lookup returned a deliberately injected 429. Cadence retried that Activity after 10 seconds. The independent graph lookup ran once.
2. After the second successful agent lookup, the capture branch copied its tool proposal and marked it blocked before dispatch. This is a controlled injection, not evidence of spontaneous model looping. The ordinary guard separately checks proposed tool names and sorted arguments, and a turn budget bounds the loop.
3. The first draft had low confidence. An automated `revise` Signal requested evidence quotes. That revision became highly confident without fetching new logs.
4. An automated `guidance` Signal directed a new investigation through payments and ledger. A second explicit `revise` Signal asked for the observed errors to be separated from the unknown trigger. Approval was still separate.
5. The recorder killed only the two Worker processes it started. Cadence and its database stayed running. Replacement Workers restored the same approval wait; no model calls were repeated. Automation then approved the report and its keyed write completed.

The final recorded fields are `root_cause: unknown` and `confidence: low`. The logs show connection exhaustion. They do not establish what triggered it. A model-written sentence excluding inventory is not independent proof that inventory could not contribute.

## Read the evidence without running services

Python 3.12 or 3.13 is sufficient. This command uses only the standard library and makes no network calls:

```sh
python3 verify_recording.py
```

It verifies frozen-file hashes, reported usage, request equality, model completions, review Signals, the retry policy, Worker identities and the final completion. See [the methodology](METHODOLOGY.md) for the comparison and its limits.

| Saved observation | Cadence Run | Uncheckpointed Python, including restart |
| --- | ---: | ---: |
| Model responses | 9 | 18 |
| Input tokens | 3,901 | 7,802 |
| Output tokens | 751 | 1,502 |
| Logical tokens | 4,652 | 9,304 |
| New model responses during recovery | 0 | 9 |

That is 50% fewer logical tokens in this recovery comparison. It is not a monetary savings measurement. Local inference has compute costs, and a Python design with persistent checkpoints can recover differently.

## Set up a fresh local capture

The following is a portable adaptation of the original controller. Runtime modules and fixtures in `source/` are unchanged. [The manifest](source-manifest.json) records every original/export hash and the controller adaptations. Portable capture and browser playback were not rerun as part of the export.

From this directory, prepare an environment with Python 3.12 or 3.13:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install
npx playwright install chromium
```

Use a local Cadence frontend on `localhost:7833`, Web on `http://localhost:8088`, and an existing local domain `incident-demo`. Domain provisioning is separate. Set `CADENCE_TARGET`, `CADENCE_WEB_URL` and `CADENCE_DOMAIN` if your local ports or domain differ.

For the recommended repository model path, pull Qwen before the event:

```sh
ollama pull qwen2.5:7b
```

Set the catalog on the controller so its Workers use the repository's existing `qwen2.5-local` selection at the normal local Ollama endpoint:

```sh
export INCIDENT_TRIAGE_CATALOG="$(cd ../../../../../ && pwd)/models.yaml"
export INCIDENT_TRIAGE_MODEL_ID=qwen2.5-local
```

The frozen `source/models.yaml` preserves the recording's isolated `qwen-local` ID and port 11435. Both select Qwen2.5:7b. Do not confuse the historical catalog ID with the repository's recommended one. The generic recipe's live default is still Llama unless explicitly selected; the live retry exercise in PR #116 selects Qwen explicitly. Smaller-model output and timing may differ.

In terminal 1:

```sh
.venv/bin/python run_capture.py
```

Wait for it to print a new Workflow/Run ID, then in terminal 2:

```sh
node record-live.cjs
```

The controller creates a fresh `capture/` and refuses to overwrite one. To make another recording, set the same new `KEYNOTE_CAPTURE_DIR` in both terminals. The recorder opens a real Cadence Web session, releases presentation pauses, sends the review Signals, stops its owned demo Workers and records browser video. Never point this fault-injection harness at a shared or production installation.

`comparison/derive_comparison.py` is the original measurement entry point with a configurable capture path. Running it after a fresh capture makes new local model calls for an uncheckpointed first execution and restart. It writes to `comparison/measured/` and refuses to reuse an existing measurement directory. New model versions, hardware, decoding and outputs may change results; do not replace the historical counts with an assumption.

## What this export does not change

The reusable recipe, its Explorer controls, the open retry exercise (#116), timeout fix (#117) and walkthrough (#154) remain separate. The final clips also contain later editing, sound cues and selected CLI history overlays. Those CLI excerpts were retrieved after this Run completed; they were not a continuous terminal recording beside the original browser. This folder exports runtime, recording and measurement code, not the deck or video editing pipeline.
