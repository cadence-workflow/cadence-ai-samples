# Find something to work on

After the Incident Triage introduction, choose a task with a maintainer.
Most contributions will be in AI samples, but you're welcome to bring a small
workflow or ask about another Cadence Issue.

## Extend a recipe

Start from what you just ran. The exercise runner's scenarios are in
[`run_exercise.py`](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/run_exercise.py);
a new failure or review case is a scenario plus its checks. To see the
commands and Signals for every recipe, run the
[Local Samples Explorer](../../tools/explorer/README.md) with
`./scripts/explore.sh` from the repository root. Pick one change with a visible
result and agree it with a maintainer before you start.

## Make an upstream contribution

Use the [ContribFest milestone](https://github.com/cadence-workflow/cadence-ai-samples/milestone/2)
and the guide's [Issue selection and claim process](../../CONTRIBFEST.md#2-claim-one-issue).
Only open, unassigned `status:ready` work is available. Check linked pull
requests and wait for the required ownership record before starting a branch.

Ask a maintainer to help choose one change with a visible result. A test might
show that an existing protection survives a lost reply. A documentation change
might let someone run the recipe without an explanation from its author.
Those examples are directions to discuss, not claims that such Issues are ready.

An existing PR may need review rather than another implementation. Ask about
another Cadence repository if its work fits you better. The same ownership,
validation and review rules apply whether you code by hand or use an agent.

## Bring a workflow of your own

Bring a small example that is safe to share. With a maintainer, identify the
model requests, tools, reads and writes that reach outside the process. Choose
one failure to handle: which result should survive, which call is safe to
repeat, and where should a person decide what happens next?

Turn one answer into a runnable step, test or design note. A complete migration
may need more time than this session. Save what you learned and the next
decision so the work can continue.

## Leave a useful result

Follow the [finish or hand off instructions](../../CONTRIBFEST.md#4-finish-or-hand-off).
Keep exact commands and results, untested behavior and the next action. Ask who
will review it. A clear handoff is useful even when the work is unfinished.
