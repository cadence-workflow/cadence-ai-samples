# Build Durable AI Agent Examples

Join Diana Zawadzki, Shijie Sheng and Cadence maintainers at KubeCon +
CloudNativeCon North America 2026.

- **When:** Wednesday, November 11, 2:20 to 3:40 PM MST
- **Where:** Salt Palace, Level 2, room 255 D, Salt Lake City

## Start with a failed checkout

You'll work with an AI agent that investigates a fictional checkout failure.
Run the existing Incident Triage example with a local model, then inspect its
work in Cadence. Which tool calls completed? What evidence reached the model?
Where does the workflow wait for a person?

The model's draft is something to review. Compare its claims with the logs
before sending guidance or approving a report. The model calls are real in
live mode; the incident and tool responses are synthetic.

From there, work with a maintainer on one small improvement: a test, clearer
instructions, a recipe change or a failure your own workflow needs to survive.
Leave the result and enough evidence for another contributor to continue.

## Choose your starting point

| If you want to... | Start here |
| --- | --- |
| Learn how agent workflows run | Follow the live example and read its history with a maintainer. |
| Make your own agent recover | Bring one small, shareable workflow and choose one call or wait to examine. |
| Contribute to Cadence | Choose an approved Issue and agree its scope and validation with the maintainer. |

Most work is in Cadence AI samples. Ask about another Cadence Issue if it fits
your interests. Coding agents are optional; you own the design and checks.

## A proposed next exercise

We are preparing a focused retry exercise: a temporary log-service failure
stops a starter, you change its policy, and Cadence retries that lookup while
keeping completed work. A separate missing-resource check should catch a
policy that retries everything. This documentation change does not add that
exercise. Its commands and availability depend on integration and rehearsal.

Until then, the existing live walkthrough below is the available starting point.
The [task list](shortlist.md) distinguishes running an example from claiming an
upstream contribution.

## Get ready

- [Set up your laptop and run Incident Triage](setup.md).
- [Choose a task or bring a workflow](shortlist.md).
- [See the proposed session outline](agenda.md).
- Follow the [participant guide](../../CONTRIBFEST.md) for claims, DCO and review.

A finished exercise, useful test, draft pull request or clear handoff is a
good outcome. You do not need to complete a migration or merge in the room.
Save what you tried, what happened and the next step.
