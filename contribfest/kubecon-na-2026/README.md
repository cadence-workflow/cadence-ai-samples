# Build Durable AI Agent Examples

Join Diana Zawadzki, Shijie Sheng and Cadence maintainers at KubeCon +
CloudNativeCon North America 2026.

- **When:** Wednesday, November 11, 2:20 to 3:40 PM MST
- **Where:** Salt Palace, Level 2, room 255 D, Salt Lake City

## What you'll do

**Bring your own workflow and make it durable.** Bring an agent or script you
already run that makes at least one model or tool call. By the end, it runs
as a Cadence Workflow and survives the failure you're most worried about.

**1. Warm up together (about 20 minutes).** Incident Triage is an AI agent
investigating a fictional checkout outage with a real local model.

- **First win:** a log lookup gets an HTTP 429 rate limit. With a Cadence
  retry policy it waits, retries and the agent carries on. No retry loop in
  your code.
- **Block the reverse:** a 404 means the resource is gone, so retrying it only
  wastes time. You make that error stop after one attempt, then check both
  outcomes in Cadence Web.

Instructions:
[retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).

**2. Make your own workflow durable (the rest of the session).**

1. Wrap: run your agent inside one Cadence Activity, started by a Workflow.
   Every run, input, result and retry shows up in Cadence Web.
2. Split: move the model call and each tool call into their own Activities,
   so each one retries on its own and finished work isn't redone.
3. Steer (stretch): add a Signal so a person can approve or redirect.

Stop at any depth. Steps and examples are in
[Find something to work on](shortlist.md#bring-your-own-workflow).

**Didn't bring one?** Take a ContribFest Issue:

| Issue | What you'll do | Level | Needs a model |
| --- | --- | --- | --- |
| [#110](https://github.com/cadence-workflow/cadence-ai-samples/issues/110) | Prove `revise` reuses evidence and `guidance` investigates again | low | no |
| [#112](https://github.com/cadence-workflow/cadence-ai-samples/issues/112) | Make the recipe's clean-copy check pass | low | no |
| [#111](https://github.com/cadence-workflow/cadence-ai-samples/issues/111) | Show a model call recovering from a rate limit | mid | yes |
| [#109](https://github.com/cadence-workflow/cadence-ai-samples/issues/109) | Help a small local model name the root cause | mid | yes |

A merged fix, a draft pull request or a written next step are all good
outcomes. You can work by hand or with a coding agent.

## Get ready

- [Set up your laptop](setup.md).
- [Find something to work on](shortlist.md).
- [See the session outline](agenda.md).

Ask a maintainer if you get stuck or want help choosing a task. The
[participant guide](../../CONTRIBFEST.md) covers claiming Issues, sign-off and
review.
