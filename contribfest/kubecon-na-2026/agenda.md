# Session outline

The listed session is November 11, 2:20 to 3:40 PM MST. We are planning a
75-minute core within that slot. The sequence below is proposed; the shared
exercise still needs a timed human rehearsal before we set the minute splits.

| Part | What we do together | What to check |
| --- | --- | --- |
| Meet and pair up | Introduce the fictional checkout incident and open Cadence Web. | Find the Workflow ID, Activity history and current state. |
| Make the retry fix | Run the prepared failure, edit one lookup policy and try again. | In the repaired run, the temporary error recovers and the graph is fetched once. The permanent-resource check stops once. |
| Compare our results | Take turns showing the lookup, a real model decision and the first review wait. | Explain what Cadence retried and why the model's draft still needs a person to review it. |
| Choose a contribution | Extend an AI sample, bring a small workflow or claim another approved Cadence Issue. | Agree one change and how to check it with a maintainer. |
| Save and share | Show what changed and leave a useful next step. | Keep the commands, actual results and a review owner. |

## Help each other through the first fix

Everyone starts with the retry exercise. Pair on a working laptop if yours
is not ready. Take turns editing and explaining; a helper can investigate
setup without taking you out of the shared activity. If your pair finishes
early, help a neighbor reach the same result before choosing the next task.

The policy edit is tested in a new Workflow. It does not resume the finished
starter run. Within that new run, only the log lookup retries; the graph is
fetched once.

The retry happens at the log lookup, before the model starts investigating.
Real inference follows the repaired lookup. This exercise demonstrates the
retry boundary; it does not establish model-token savings.

## Pause at the first review

Show the model's returned action and the lookup that the Worker actually
executed. Compare a draft claim with the logs. The first draft waits in
`AWAITING_GUIDANCE`, before final approval. Explain what input it needs next.
Close the bounded exercise with its explicit rejection step; this does not
approve or upload a report.

Sending guidance to the Workflow is a separate reviewer action. Cadence calls
this a Signal. If you continue into the full review flow, read the payload
together, send it, then inspect the state change. Do not describe an automated
test action as a person rehearsing.

## If live execution is unavailable

First try pairing on a prepared machine. If the room cannot run the example,
inspect a clearly labeled recording and history together. Ask each pair to
identify the failed lookup and explain the retry decision. That keeps the
discussion shared, but it does not establish a working participant runtime.

Internet access and local model readiness are different dependencies. The
offline path requires downloaded packages, container images and model weights,
plus a full rehearsal with networking disabled.

## Save the next step

Use the [task list](shortlist.md) and [participant guide](../../CONTRIBFEST.md)
when moving from the exercise to upstream work. Agree a review owner and
follow-up date. Keep unfinished work understandable rather than rushing to
finish a pull request in the room.
