# Proposed session outline

The listing is November 11, 2:20 to 3:40 PM MST. This working outline uses a
75-minute core within that slot; final pacing remains for the hosts to confirm.

| Time from the start | What we do | What you can see |
| --- | --- | --- |
| 0 to 10 minutes | Watch a short Incident Triage demonstration | A model request, a tool result, review and the work Cadence records. |
| 10 to 25 minutes | Check setup and choose a task | A running baseline, a pairing plan or a confirmed Issue. |
| 25 to 65 minutes | Work with maintainers | One change, its validation and an explanation of what now works. |
| 65 to 75 minutes | Save progress and share what changed | An exercise result, test, draft pull request or clear handoff. |

## Watch the boundaries

The presenter identifies synthetic data, real model calls and deliberately
introduced failures. When a reviewer sends a Signal, watch its payload and
then the state that follows. If the demonstration uses recorder automation,
name that role instead of describing it as a person rehearsing.

For a Worker-loss demonstration, keep Cadence running. Compare the Workflow
and Run IDs and actual model receipts before and after replacement. Reusing
a recorded model Activity result is different from calling the model again.
A model call whose completion was not recorded can be retried.

## Work and ask for help

Use the [task list](shortlist.md) and [setup instructions](setup.md). Ask for a
smaller task when setup or scope blocks progress. Before editing, describe the
failure, the change and what you expect to see afterward. Keep the evidence
even if the change does not work yet.

If the live demonstration cannot run, use a local recording and identify it
as a recording. A scripted check is useful for its own purpose; say clearly
when it does not call a model. Internet access and local model readiness are
different dependencies.

## Save the next step

Show one thing you learned or changed. Use the normal guide to hand off your
branch, commands, actual results and remaining questions. Agree a review owner
and follow-up date rather than assuming unfinished work will be picked up.
