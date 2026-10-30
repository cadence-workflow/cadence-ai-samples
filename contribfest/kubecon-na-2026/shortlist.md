# Find something to work on

Do the [retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md)
first. Every Issue below starts from it.

## ContribFest Issues

| Issue | What you'll do | Cadence idea | Level | Needs |
| --- | --- | --- | --- | --- |
| [#110](https://github.com/cadence-workflow/cadence-ai-samples/issues/110) | Test that `revise` reuses evidence and `guidance` investigates again | Signals, Queries, Workflow tests | low | Python only |
| [#112](https://github.com/cadence-workflow/cadence-ai-samples/issues/112) | Make the Incident Triage clean-copy check pass | Self-contained samples | low | Python only |
| [#111](https://github.com/cadence-workflow/cadence-ai-samples/issues/111) | Show a model call recovering from a rate limit | Activity retry policy | mid | Cadence, Ollama, `qwen2.5:7b` |
| [#109](https://github.com/cadence-workflow/cadence-ai-samples/issues/109) | Help llama3.2 name the root cause, not the symptom | Human review of agent output | mid | Cadence, Ollama, `llama3.2` and `qwen2.5:7b` |

Each Issue explains the problem, shows the command that reproduces it, names the
file to change and says how to check the fix. Issues #109 and #111 need the
exercise merged first; the Issue says so at the top.

To claim one:

1. Check it is open, unassigned and labeled `status:ready`, with no linked pull request.
2. Comment on the Issue with your GitHub username and your branch name, `issue-N-short-slug`.
3. Wait for the claim coordinator to assign you and change the label to `status:in-progress`.
4. Create the branch in your fork, commit with `git commit -s`, and open a pull request against `main`.

The full process is in [CONTRIBFEST.md](../../CONTRIBFEST.md#2-claim-one-issue).
The [ContribFest milestone](https://github.com/cadence-workflow/cadence-ai-samples/milestone/2)
has the current list.

## Extend the exercise

Every scenario in
[`run_exercise.py`](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/run_exercise.py)
is a prepared failure plus the checks that prove Cadence handled it. To add one,
for example an approval that never arrives (a durable timer) or a write whose
reply is lost (an idempotency key), copy the `rate-limit` scenario, change the
failure, and write its checks. Open an Issue describing it before the pull
request.

## Bring your own agent

Bring a small agent or workflow that's safe to share. With a maintainer:

1. List every model call and tool call that leaves the process.
2. Pick the one most likely to fail, and decide whether a retry is safe.
3. Make it a Cadence Activity with a retry policy and a timeout, or add a
   Signal where a person should approve.
4. Run it, break that call on purpose, and check the result in Cadence Web.

If it doesn't finish in the session, write down the commands, what works and
the next step, and open an Issue so someone can continue.

## Leave a useful result

Follow the [finish or hand off instructions](../../CONTRIBFEST.md#4-finish-or-hand-off).
