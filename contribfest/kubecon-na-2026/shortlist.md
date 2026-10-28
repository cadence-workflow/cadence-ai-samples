# Choose something to work on

Choose based on what you want to learn and which Issues are available. Start
with the [live Incident Triage walkthrough](setup.md) if you are new to Cadence.
It gives you a running example to inspect before you change one of your own.

## Run and understand the example

Find the model Activity, a completed tool lookup and the point where the
workflow waits for review. Compare a draft with the logs. Send guidance or a
revision request and check which state changes. If you stop here, reject the
run explicitly rather than leaving it waiting without a next step.

Running the same walkthrough is useful for many learners. It is a teaching
activity, not a separate upstream Issue for every person.

The proposed broken-lookup retry exercise is a follow-up to these pages. It
still needs its repository integration and rehearsal before it can appear as
an available task. Do not look for its commands in the current recipe.

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
