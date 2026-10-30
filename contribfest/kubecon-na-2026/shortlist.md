# Find something to work on

Start with the [retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).
Then [bring your own workflow](#bring-your-own-workflow), or take a ContribFest
Issue below if you didn't bring one.

## Choose a ContribFest Issue

Pick a recipe task from the [approved ContribFest pool](https://github.com/cadence-workflow/cadence-ai-samples/issues?q=is%3Aissue%20is%3Aopen%20milestone%3A%22KubeCon%20NA%202026%20ContribFest%2C%202026-11-11%22%20label%3Aevent%3Acontribfest%20label%3Astatus%3Aready%20no%3Aassignee%20label%3Aarea%3Arecipes%20label%3Aformat%3Ahuman-first).
Each task should tell you what to run, what to change and how to check your
work. Choose one that fits your setup and the time you have.

A task is available only while it is open, unassigned and labeled
`status:ready`, with no existing claim or active implementation PR. If the
list is empty, ask a facilitator for a task.

Before you start, comment on the Issue:

> I'd like to take this. GitHub: @yourname. Proposed branch:
> `issue-N-short-slug`.

Wait for the coordinator to record you as the owner and change the label to
`status:in-progress`, then create your branch. The
[claim guide](../../CONTRIBFEST.md#2-claim-one-issue) covers the full process.

### Keep the recipe useful to the next developer

Someone may copy one recipe into their own project. For
[#112](https://github.com/cadence-workflow/cadence-ai-samples/issues/112), the
clean-copy check must pass, and the catalog tests must still run in a full
checkout. Removing those tests is not a fix. The Issue has the files and
commands to check both cases.

## Extend the exercise

Every scenario in
[`run_exercise.py`](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/run_exercise.py)
is a prepared failure plus the checks that prove Cadence handled it. To add one,
for example an approval that never arrives (a durable timer) or a write whose
reply is lost (an idempotency key), copy the `rate-limit` scenario, change the
failure, and write its checks. Open an Issue describing it before the pull
request.

## Bring your own workflow

Start from [#118](https://github.com/cadence-workflow/cadence-ai-samples/issues/118). Open your own Issue titled
`<Example> Make <your agent> durable`, so it can be claimed, reviewed and
continued by someone else.

Bring a small agent or script that's safe to share and makes at least one
model or tool call. Work through as many depths as you have time for:

1. **Wrap.** Start a Workflow that runs your agent in one Activity and returns
   its output. Run it and find it in Cadence Web.
2. **Break it.** Pick the call most likely to fail (a rate-limited API, a slow
   model, a flaky tool). Make it fail on purpose and watch what happens.
3. **Make it durable.** Move that call into its own Activity with a retry
   policy and a timeout. Mark errors a retry can't fix as non-retryable.
4. **Steer (stretch).** Add a Signal so a person approves before the agent
   acts.

The [Incident Triage recipe](../../recipes/incident-triage/python/bare/workflow.py)
shows every step: model and tool calls as Activities, retry policies,
non-retryable errors and review Signals. Copy from it.

If you don't finish, write down the commands, what works and the next step,
and open an Issue so someone can continue.

## Explore and file what you find

[#119](https://github.com/cadence-workflow/cadence-ai-samples/issues/119): run Incident Triage in mock mode, stop the worker mid-run,
send Signals, run two at once. Open a `<Finding>` Issue for anything that
surprised you. No model needed.

## Leave a useful result

Follow the [finish or hand off instructions](../../CONTRIBFEST.md#4-finish-or-hand-off).
