# How maintainers choose tasks

Choose small, useful work from the actual repository. Read the code and run
the task before offering it. The [participant guide](../../CONTRIBFEST.md)
remains authoritative for claims, sign-off, validation and review.

## Start with a result someone can see

A learner should be able to name the starting behavior, the change they make
and the evidence that it worked. For the proposed retry exercise, that means
a failed lookup, a bounded policy edit and a recovered lookup that preserves
completed work. A permanent-error case should catch an overbroad retry policy.
That exercise needs separate integration and rehearsal; this PR adds pages.

Use the selection approach in
[cert-manager's ContribFest methods](https://github.com/cert-manager/website/blob/master/content/docs/contributing/contribfest-kubecon-eu-2026/methods.md)
to ask whether the scope fits the session, the instructions are clear and the
result rewards the contributor while helping the project. Write Cadence's
tasks from its actual code and needs.

## Verify the offered path

For each task, keep the source revision, prerequisites, commands, expected
result, stopping point and cleanup. Check the application outcome as well as
service completion. A handled unavailable input can complete a workflow
without completing an investigation.

A real-model path needs actual returned responses and usage. Mock tests and
the scripted comparison have different evidence. Human rehearsal means a
person follows the Issue alone; record coaching as a finding. Downloading a
source archive is not a full disconnected rehearsal.

## Keep one source for ownership

Use upstream Issues and PRs for readiness and claims. Recheck open PRs and
assignees before listing work, and recheck availability on the session day.
Do not maintain another authoritative queue in this page. Count a repeatable
exercise once as a teaching asset, separately from independent contributions.

The November 4 pool freeze should confirm tested tasks and reviewers. If the
target exceeds ready work, resolve the target with maintainers instead of
counting duplicate or untested tasks. Agree who reviews unfinished work and
when to follow up. Record actual event findings afterward.
