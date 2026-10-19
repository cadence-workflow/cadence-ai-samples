# Incident Triage

This recipe follows one fictional checkout failure twice. First, a capable
plain-asyncio agent loses its in-memory work after a process interruption.
Then the same synthetic incident, scripted planner, tools, guidance, changed
brief, approval, and fault schedule run as a Cadence Workflow.

The teaching result is preserved state and less repeated work. It is not a
speed, token, cost, or exactly-once claim.

## What the agent does

The agent starts from one failed API trace. It reads gateway logs and a
dependency graph, follows errors through checkout, payments, and ledger, accepts
operator guidance and a changed output brief, waits for approval, and writes one
keyed conclusion.

The fixtures and planner are deterministic and synthetic. No provider,
tokenizer, credential, paid API, or production data is used.

## Requirements

- Python 3.12 or 3.13.
- The published `cadence-python-client` 0.4.1 release.
- Cadence at `localhost:7833` with domain `cadence-ai-samples` for Worker,
  rehearsal, variant, and comparison commands.

## Setup and offline tests

From this directory:

```bash
./run.sh setup
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python durability_manifest.py
.venv/bin/python check_clean_copy.py
```

The tests and line-manifest check are offline.

## Run through the generic recipe interface

Terminal 1:

```bash
./run.sh worker --mode mock
```

Terminal 2:

```bash
./run.sh start --mode mock
```

Both `mock` and `live` use the same provider-free synthetic Activities. The
`live` mode preserves the repository's generic `worker|start --mode mock|live`
shape; it does not call a model provider.

The Workflow waits first for a `guidance` Signal and later for an `approval`
Signal. `explorer.yaml` exposes guidance, revision, and approval controls in the
Local Samples Explorer.

## Run the durability rehearsal

```bash
.venv/bin/python run_rehearsal.py --evidence .evidence/rehearsal
```

The self-checking rehearsal injects one HTTP 429, bounds the tool loop, changes
the brief, corrects the wrong answer with guidance, kills every Worker during
the approval wait, restarts Workers, and approves the conclusion. It fails
unless setup Activities remain recorded, no Activity runs during the
zero-worker interval, the final answer is correct, and one keyed write occurs.

Run the five bounded endings:

```bash
.venv/bin/python run_variants.py --evidence .evidence/variants.json
```

They cover approval expiration, rejection, a nonretryable graph 404, planning
budget exhaustion, and a committed write whose first reply is lost.

## Compare raw asyncio with Cadence

```bash
.venv/bin/python run_compare.py
.venv/bin/python verify_comparisons.py --count 3
```

The command runs raw first and then the local Cadence rehearsal. It prints one
human-readable table and writes a machine-readable record under
`.evidence/compare-runs/`. The checked-in
[`evidence/comparison-baseline.json`](evidence/comparison-baseline.json) retains
three sanitized runs and their exact provenance.

Expected deterministic counters for this fault schedule are:

- observed scripted model calls: raw 15, Cadence 11;
- repeated tool calls: raw 15, Cadence 3;
- completed setup steps redone after interruption: raw 8, Cadence 0;
- observed final writes: one on each path;
- duplicate uploads: zero on each path.

Wall time is measured, retained, and expected to vary. Local Cadence is slower
in the current short scripted harness because orchestration overhead dominates
subsecond synthetic work. The table says so. No fixed per-call multiplier is
reported as tokens or cost. The useful provenance is the observed `plan_next`
and `revise_draft` ledger entries.

## Fairness and line counts

The raw baseline has bounded retry with backoff, exception handling, a turn
limit, an in-process changed-brief task, in-memory state, process-local write
deduplication, and a live approval wait. It is not deliberately weakened.

`durability-lines.json` classifies retry, state, and deduplication lines in
`raw_agent.py` and `workflow.py` using the same rules. Every entry includes its
file, line range, category, and rationale; the validator rejects overlaps,
comments, blank lines, invalid ranges, and paths outside the recipe. These
counts describe handwritten orchestration plumbing, not total code size or SDK
internals. They are evidence, not a promise that every Cadence example has fewer
source lines.

## Workflow ID reuse

`start` uses `incident-triage-demo` with `ALLOW_DUPLICATE`. A new Run may reuse
the ID after the previous Run closes. Cadence rejects a duplicate while a Run is
open, and the CLI reports that condition. Use another `--workflow-id` when you
want concurrent runs.

## Copying the recipe

Copy the complete `recipes/incident-triage` directory. The implementation does
not import another recipe or repository-only runtime code. Keep nondeterministic
work and side effects in Activities, preserve the idempotency key on the final
write, and replace the synthetic fixtures only with data safe for your
application.

If the launcher cannot prepare the environment, run:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e .
```
