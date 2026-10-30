# Build Durable AI Agent Examples

Join Diana Zawadzki, Shijie Sheng and Cadence maintainers at KubeCon +
CloudNativeCon North America 2026.

- **When:** Wednesday, November 11, 2:20 to 3:40 PM MST
- **Where:** Salt Palace, Level 2, room 255 D, Salt Lake City

## What you'll do

**1. Fix an AI agent's retry policy (everyone, about 25 minutes).** Incident
Triage is an AI agent investigating a fictional checkout failure with a real
local model. You'll watch it look up logs service by service in Cadence Web.
Then a log lookup fails with HTTP 429 and the agent stops before it starts
reasoning. You fix that by editing one file, the lookup's retry policy, and run
it again: the 429 recovers, a permanent 404 still stops, and the agent reaches
a draft for you to review. The incident and API failures are synthetic; the
model calls are real. Instructions:
[retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).

**2. Take one ContribFest Issue (the rest of the session).** Each one builds on
the exercise and has a command that shows the problem, the file to change and
how to check your fix:

| Issue | What you'll do | Level | Needs a model |
| --- | --- | --- | --- |
| [#110](https://github.com/cadence-workflow/cadence-ai-samples/issues/110) | Write a test proving `revise` reuses evidence and `guidance` investigates again | low | no |
| [#112](https://github.com/cadence-workflow/cadence-ai-samples/issues/112) | Make the recipe's clean-copy check pass, so one recipe can be copied on its own | low | no |
| [#111](https://github.com/cadence-workflow/cadence-ai-samples/issues/111) | Show a model call recovering from a rate limit through its Cadence retry policy | mid | yes |
| [#109](https://github.com/cadence-workflow/cadence-ai-samples/issues/109) | Help the smaller llama3.2 model name the root cause, not the symptom | mid | yes |

The full list is the
[ContribFest milestone](https://github.com/cadence-workflow/cadence-ai-samples/milestone/2).
Claim an Issue before you start: see [Find something to work on](shortlist.md).

**Or bring your own agent.** If you have a small agent or workflow that's safe
to share, we'll find its model calls and tool calls with you, pick the one most
likely to fail, and give it a Cadence retry policy, a timeout or a human
approval step.

You can work by hand or with a coding agent. A merged fix, a draft pull request
or a clear handoff are all good outcomes.

## Get ready

- [Set up your laptop](setup.md).
- [Find something to work on](shortlist.md).
- [See the session outline](agenda.md).

Ask a maintainer if you get stuck or want help choosing a task. The
[participant guide](../../CONTRIBFEST.md) covers claiming Issues, sign-off and
review.
