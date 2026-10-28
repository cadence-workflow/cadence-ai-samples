# Build Durable AI Agent Examples

Join Diana Zawadzki, Shijie Sheng and Cadence maintainers at KubeCon +
CloudNativeCon North America 2026.

- **When:** Wednesday, November 11, 2:20 to 3:40 PM MST
- **Where:** Salt Palace, Level 2, room 255 D, Salt Lake City

## Make the first fix together

We'll start with Incident Triage, an AI agent investigating a fictional
checkout failure. A log lookup has an intentional rate-limit failure. You'll
inspect it in Cadence Web and change its retry policy so the lookup can
recover. In the repaired run, check that Cadence retries the log lookup while
fetching the graph once. Then follow the real model's investigation to a draft
for review.

Work in pairs and take turns driving. Before choosing another task, show each
other what failed, what you changed and why the new policy let it continue.
Then check a permanently missing resource: the same request should stop,
rather than retrying an error it cannot repair.

The model calls are real. The incident data and API failures are synthetic,
so everyone can work on the same failure without waiting for a model to make
a particular mistake. Model choices and drafts can differ. Compare the draft
with its source logs before accepting its claims.

The shared exercise is being integrated and rehearsed. The [setup page](setup.md)
explains which commands run the existing example today.

## Choose what to work on next

After we compare our results, choose a contribution with a maintainer.

| What interests you? | What you can work on |
| --- | --- |
| More AI examples | Extend Incident Triage or another sample with a useful change and a result someone can check. |
| Your own agent workflow | Bring a small, shareable example and work on one call or wait that needs to survive failure. |
| Another part of Cadence | Ask about an available, approved Issue that fits your interests. |

Most work will be in Cadence AI samples. You can work by hand or use a coding
agent; you own the design and checks either way. If setup blocks you, pair on
a working laptop so you can stay with the shared exercise.

## Get ready

- [Set up your laptop](setup.md).
- [Find your next contribution](shortlist.md).
- [See the session outline](agenda.md).
- Follow the [participant guide](../../CONTRIBFEST.md) for claims, DCO and review.

A useful recipe, test, draft pull request or clear handoff is a good outcome.
Save what you tried, what happened and what the next contributor needs to know.
