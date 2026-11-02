# Working on a ContribFest Issue

Every ContribFest Issue links here for the parts they share. Read the section
you need when an Issue points to it.

## Before you start

1. Finish [setup](setup.md) and the
   [retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).
   Most Issues build on what you saw there: a 429 retried by Cadence, a 404
   stopped after one attempt, the repeated-call guard, and the `revise` and
   `guidance` Signals.
2. Claim the Issue as [the shortlist](shortlist.md) describes.
3. Run the recipe's own setup once, from the directory the Issue names:
   `./run.sh setup` (Python and Go recipes both have it).

## Run your own Worker

Other people's Workers may be polling the same server. Give your Worker and your
Runs your own names:

```bash
./run.sh --task-list <you>-<recipe> worker --mode mock                   # terminal 1
./run.sh --task-list <you>-<recipe> --workflow-id <you>-1 start --mode mock   # terminal 2
```

In Python recipes, `--task-list` and `--workflow-id` are global flags. They go
**before** the subcommand, or `run.sh` rejects them.

Go recipes are the other way round: flags go **after** the subcommand, and
`-mode` is required. `-workflow-id` exists only on `start`. Flags before the
subcommand fail with `unexpected arguments`:

```bash
./run.sh worker -mode mock -task-list <you>-tickets                     # terminal 1
./run.sh start -mode mock -task-list <you>-tickets -workflow-id <you>-1  # terminal 2
```

The default task list and Workflow ID are shared names, so always pass your own.

**Optional: the Samples Explorer.** If you'd rather click than type, run
`./scripts/explore.sh` from the repository root. Nothing in an Issue
requires it; it's there to help you find your way around and see what a
Run is doing. Choose the recipe, language and mode, then **Refresh
and check services**. It prints the Worker and start commands for you to copy;
it doesn't run them. Choose the mode explicitly: there is no default. After
you start a Run, **Resolve latest run** shows its Cadence Web links and the
recipe's Signal buttons. Each Signal asks you to **Confirm** before it sends.

The Explorer's commands use fixed names (for example
`--task-list incident-triage-python-bare-mock`). That's fine on your own laptop's
Cadence. On a shared server, edit the names before you run them, and note that a
second `start` fails while the demo Run is still open. Ticket Routing has no Signal buttons: acknowledge from the
parent's `ticket-assignment` Query in Cadence Web instead.

## Find your Run in Cadence Web

Open `http://localhost:8088/domains/cadence-ai-samples/cluster0/workflows/<workflow-id>`
(add `/<run-id>/history` for one Run), or use the Explorer's **Open history**.

- **History** lists every Activity. A retried Activity shows `1 Retry` (or
  more) and still ends `Completed` when a later attempt succeeds.
- **Queries** runs a read-only Query such as `status`. Click **Run**.
- A Run waiting for a Signal or timer is `Running` with no Activity in
  progress. No Worker is busy while it waits.
- A Signal sent while your Worker is stopped is still accepted
  (`WorkflowExecutionSignaled` in History) and handled after the Worker
  restarts.
- **Queries need a running Worker.** With no Worker, `status` times out with
  `deadline-exceeded`.
- In the raw history a retried Activity has one scheduled event. The attempt
  number (counting from 0) is on its `ActivityTaskStarted` event.

## Who does what

Issues say which part of the behavior comes from where. Keep the three apart
when you explain your change:

| Part | Decides | Example |
| --- | --- | --- |
| **The model** | What to look up next, what the draft says | qwen2.5 picks `payments` after `checkout` |
| **Recipe code** | Which tools exist, guards, validation, what's saved | the repeated-call guard, the JSON schema, an idempotency key |
| **Cadence** | Retries, timeouts, timers, Signal delivery, history, replay after a Worker restart | the 429 retried by the Activity's retry policy |

## Write a check that tells the difference

A good check fails on `main` and passes with your change. Passing the existing
tests only proves you didn't break them.

1. Write the check before the change, run it, and keep the failing output.
2. Make the change and run it again.
3. Optional: undo one line of your change and confirm the check fails again.

Traps we hit while testing these Issues:

- **The Python test environment** (`TestWorkflowEnvironment`) doesn't retry
  Activities, so it can't count attempts. Assert on the retry options the
  Workflow passes, or count attempts against local Cadence. The Go `testsuite`
  environment is different: it does apply the retry policy.
- **The same environment fires a pending timer** as soon as the Workflow would
  otherwise block. A new deadline must default to "none", or every existing test
  that waits for a Signal ends as expired.
- **`non_retryable_error_reasons` matches the exception class name**, not its
  message. Use a dedicated exception class.
- **A retry policy needs `backoff_coefficient`.** With `initial_interval` and no
  coefficient, Cadence rejects the decision (`BackoffCoefficient cannot be less
  than 1`). Copy the shape of `QUICK_ACTIVITY` in the recipe's `workflow.py`.
- **Incident Triage pins line numbers.** `durability-lines.json` lists lines of
  `workflow.py`, so adding or removing a line there makes
  `test_manifest_is_symmetric_and_has_no_overlaps` fail. Replace lines in
  place, or update the manifest in the same change.
- **Mock Workers keep state** in the recipe's `.state/` folder across runs.
  Clear it before you count anything.
- **Go replay from a JSON history** has its own traps. See
  [Go replay from JSON](#go-replay-from-json).
- **Go `-run` is a regular expression** over every test name. Give your test a
  distinctive name, and filter the noisy output:
  `go test ./... -run X -v 2>&1 | grep -E '^\s*(---|FAIL|ok|Error:)'`.
- **In Go, a plain `error` is retried** (its reason is
  `cadenceInternal:Generic`). `cadence.NewCustomError(reason, details)` has
  `Error()` equal to the reason; read the text with `Details(&s)`.

## Cadence CLI

The host `cadence` binary needs extra configuration, so use the one in the
container:

```bash
cadence() { docker exec cadence cadence --address cadence:7933 "$@"; }
cadence --domain cadence-ai-samples workflow describe -w <workflow-id>
```

`--of <file>` writes inside the container. Copy the file out with
`docker exec cadence cat /tmp/h.json > h.json`.

## Go replay from JSON

- `ReplayWorkflowHistoryFromJSON` runs under Workflow ID `ReplayId`. Record the
  history under that ID: the ID also sits inside encoded payloads, so editing
  the JSON text doesn't work. Child IDs derive from the parent's.
- After one successful `ReplayId-child-billing`, recording again in the same
  domain fails with `WorkflowExecutionAlreadyStarted`. Record in a throwaway
  domain: `cadence --domain <you>-replay domain register --rd 1`, then pass
  `-domain <you>-replay`.
- A Worker binary records type names as `main.*`; under `go test` they carry the
  package path. Rewrite `"name":"main.` in the JSON to the test's package path.
- Client v1.3.1 can't parse `"cause":"Timeout"` on `DecisionTaskTimedOut`.
  Commit histories recorded from a run without a Worker crash.
- A change that breaks replay fails as `nondeterministic workflow` (an extra
  Activity) or `replay workflow doesn't return the same result`.

## Live models

The retry exercise and Issues marked **Needs: Ollama** call a real local model
through Ollama. Don't replace the model with a stub in those Issues: the
point is to see what a real model does.

- The exercise runner defaults to `qwen2.5:7b` (`--model-id qwen2.5-local`).
  A live Worker started with `./run.sh ... worker --mode live` (and the
  Explorer's live commands) defaults to `llama3.2-local` unless you set
  `INCIDENT_TRIAGE_MODEL_ID=qwen2.5-local`. `llama3.2` is smaller and often
  names the symptom instead of the cause.
- Requests use temperature 0, so the same input usually gives the same output.
  Run three times anyway before you trust a result.
- Each model call that returns prints a `SPEND` line with the tokens the model
  reported. That's how you measure repeated model work. A failed attempt, or a
  call lost with its Worker, prints none, so `SPEND` lines under-count the work
  the model actually did.
- **How long it takes without a GPU:** loading a model the first time adds about
  a minute, and a warm baseline run takes 20–30 s. The `review` scenario can take
  about four minutes and once hit its 30 s revise timeout under load, so Issues
  name the scenarios to run instead of `--scenario all`.

## Stuck or out of time

Stop at about 45 minutes. Push your branch, then comment on the Issue with the
branch name, the commands you ran, what works, and the next step. That
handoff is a useful contribution: the next person starts where you stopped.
