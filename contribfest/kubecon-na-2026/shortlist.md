# Choose what to work on next

First, everyone makes the Incident Triage retry fix together. We'll compare
the results before choosing separate contributions, so you can start the next
task with someone who has worked through the same problem.

## Finish the shared exercise

With your partner, show the failed lookup, your policy edit and the recovered
result. Explain why the permanently missing resource should stop once. Find
one real model decision and its executed lookup, then compare the draft with
the logs at the first review wait. Take turns explaining what happened.

The first wait is `AWAITING_GUIDANCE`, before final approval. Follow the
exercise's explicit rejection step when you finish this bounded activity.
Many people can run the same exercise. It is one teaching asset, not a new
upstream Issue for each participant.

The retry exercise still needs integration and human rehearsal. The
[setup page](setup.md) identifies the existing live example and the remaining
exercise work. Do not assume an unmerged exercise command is available.

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
