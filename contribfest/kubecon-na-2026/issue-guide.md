# ContribFest development guide

## Before you start

1. [Choose an Issue](shortlist.md) and check its prerequisites. Mock-mode tasks
   do not need Ollama; some tests do not need a running Cadence server.
2. Follow [setup](setup.md) for the services your task needs, then run
   `./run.sh setup` from the recipe directory named in the Issue.
3. [Claim the Issue](shortlist.md#contribfest-issues) before changing the code.

For an introduction to Activity retries, try the
[retry-policy exercise](https://github.com/cadence-workflow/cadence-ai-samples/pull/116).
It uses a temporary HTTP 429 and a permanent 404 to show which failures should
be retried. The exercise is being prepared in that PR.

## Run your own Worker

A [Worker](https://cadenceworkflow.io/docs/python-client/workers/) runs your
Workflow and Activity code. Cadence sends it work through a
[task list](https://cadenceworkflow.io/docs/concepts/task-lists/). On a shared
server, use a task list unique to you so another participant's Worker does not
pick up your tasks. Use the same name when starting the Workflow.
Replace `<you>` and `<recipe>` below with your own names:

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
second `start` fails while the demo Run is still open. Ticket Routing has no
Explorer Signal buttons. In Cadence Web, run the parent's `ticket-assignment`
Query and click **Acknowledge Ticket**, as the
[recipe instructions](../../recipes/ticket-routing/README.md#cadence-web-cwc) describe.

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

## Cadence concepts in the exercises

The recipes put model and tool calls in
[Activities](https://cadenceworkflow.io/docs/concepts/activities/), coordinated
by a [Workflow](https://cadenceworkflow.io/docs/concepts/workflows/). Cadence
records Activity results so a Workflow can recover after a Worker restart.
The recipe still defines validation, tool access and how to handle model output.

Use the documentation for the change you are making:

| If your Issue involves... | Read | Apply it to the recipe |
| --- | --- | --- |
| A rate-limited or failing call | Activity retries: [Python](https://cadenceworkflow.io/docs/python-client/retries/), [Go](https://cadenceworkflow.io/docs/go-client/retries/) | Set a retry policy on the Activity. Check that a temporary failure recovers and a permanent error stops. |
| Approval or new guidance | Signals: [Python](https://cadenceworkflow.io/docs/python-client/signals/), [Go](https://cadenceworkflow.io/docs/go-client/signals/) | Send input to the running Workflow, then check how its state changes. |
| Inspecting a running agent | [Queries](https://cadenceworkflow.io/docs/concepts/queries/) | Read Workflow state without changing it. Use the Query named in your recipe. |
| An approval that never arrives | [Durable timers](https://cadenceworkflow.io/docs/concepts/timers/) | Add a deadline to the wait and test both approval and expiry. |
| A write whose reply is lost | [Activity execution](https://cadenceworkflow.io/docs/concepts/activities/) | Check whether retrying the write repeats its side effect. |
| A Workflow change that must preserve existing Runs | [Go replay codelab](https://cadenceworkflow.io/docs/codelabs/workflow-tests-go-replayer-shadower/) | Replay a recorded history against the changed Workflow. |

## Write a check that tells the difference

Add a regression test that fails before your fix and passes after it. For example,
a retry-policy test should distinguish a temporary failure from a permanent one.
The SDK testing guides show how to mock Activities and test Workflow behavior:
[Python](https://cadenceworkflow.io/docs/python-client/testing/) and
[Go](https://cadenceworkflow.io/docs/go-client/workflow-testing/).

1. Write the check before the change, run it, and keep the failing output.
2. Make the change and run it again.
3. Optional: undo one line of your change and confirm the check fails again.

Recipe and SDK details to check when a test behaves unexpectedly:

- **The Python test environment used by these recipes** (`TestWorkflowEnvironment`) doesn't retry
  Activities, so it can't count attempts. Assert on the retry options the
  Workflow passes, or count attempts against local Cadence. The Go `testsuite`
  environment is different: it does apply the retry policy.
- **The same environment fires a pending timer** as soon as the Workflow would
  otherwise block. When adding a deadline, check tests that wait for Signals:
  virtual time may advance to expiry before they send the Signal.
- **`non_retryable_error_reasons` matches the exception class name**, not its
  message. Use a dedicated exception class.
- **Set `backoff_coefficient` explicitly with the recipe's Python SDK.** In the
  tested setup, with `initial_interval` and no
  coefficient, Cadence rejects the decision (`BackoffCoefficient cannot be less
  than 1`). Copy the shape of `QUICK_ACTIVITY` in the recipe's `workflow.py`.
- **Incident Triage pins line numbers.** `durability-lines.json` lists lines of
  `workflow.py`, so adding or removing a line there makes
  `test_manifest_is_symmetric_and_has_no_overlaps` fail. Replace lines in
  place, or update the manifest in the same change.
- **Mock Workers keep state** in the recipe's `.state/` folder across runs.
  Use a fresh test state when checking write counts; preserve any state you need
  for a restart or lost-reply test.
- **Go replay from a JSON history** has its own traps. See
  [Go replay from JSON](#go-replay-from-json).
- **Go `-run` is a regular expression** over every test name. Give your test a
  distinctive name, and filter the noisy output:
  `go test ./... -run X -v 2>&1 | grep -E '^\s*(---|FAIL|ok|Error:)'`.
- **With a retry policy in Go, a plain `error` is retryable** (its reason is
  `cadenceInternal:Generic`). `cadence.NewCustomError(reason, details)` has
  `Error()` equal to the reason; read the text with `Details(&s)`.

## Cadence CLI

The [Cadence CLI](https://cadenceworkflow.io/docs/cli/) can describe Runs and
export history. If your local server container is named `cadence`, you can use
its bundled CLI:

```bash
cadence() { docker exec cadence cadence --address cadence:7933 "$@"; }
cadence --domain cadence-ai-samples workflow describe -w <workflow-id>
```

`--of <file>` writes inside the container. Copy the file out with
`docker exec cadence cat /tmp/h.json > h.json`.

## Go replay from JSON

The [replay codelab](https://cadenceworkflow.io/docs/codelabs/workflow-tests-go-replayer-shadower/)
explains how a recorded history detects incompatible Workflow changes. The
following details apply to the Ticket Routing exercise using Go client v1.3.1:

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
- Requests use temperature 0, which does not guarantee identical output. Keep the model ID
  and output with a report of model-dependent behavior.
- Each model call that returns prints a `SPEND` line with the tokens the model
  reported. That's how you measure repeated model work. A failed attempt, or a
  call lost with its Worker, prints none, so `SPEND` lines under-count the work
  the model actually did.

Model speed depends on your laptop and the scenario. If a call times out, keep
the error and ask a maintainer to help distinguish a slow model from a Workflow
or Activity timeout.

<a id="stuck-or-out-of-time"></a>

## Get help or share your progress

Ask a maintainer if a command fails or the behavior is unclear. Include the
command, error output and Workflow ID if there is one. Never post API keys or
private model inputs.

You can open a draft PR for unfinished work. Describe what you tested and what
still needs work, and link it from the Issue. Follow the
[contribution instructions](../../CONTRIBFEST.md#4-finish-or-hand-off) for
sign-off and review. Your fix will help future Cadence users build on these
samples.
