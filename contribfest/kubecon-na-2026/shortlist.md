# Find something to work on

Start with the [retry-policy exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).
For your contribution, [bring your own workflow](#bring-your-own-workflow), or
take a ContribFest Issue below if you didn't bring one.

<a id="choose-a-contribfest-issue"></a>

## ContribFest Issues

Check the [approved recipe tasks](https://github.com/cadence-workflow/cadence-ai-samples/issues?q=is%3Aissue%20is%3Aopen%20milestone%3A%22KubeCon%20NA%202026%20ContribFest%2C%202026-11-11%22%20label%3Aevent%3Acontribfest%20label%3Astatus%3Aready%20no%3Aassignee%20label%3Aarea%3Arecipes%20label%3Aformat%3Ahuman-first) for work that fits your setup.
A task is available while it is open, unassigned and labeled `status:ready`,
with no existing claim or active implementation PR. If the pool is empty,
ask a facilitator about another approved task or explore a sample while you wait.

For alternatives such as Java profile CI, browse
[all approved event tasks](https://github.com/cadence-workflow/cadence-ai-samples/issues?q=is%3Aissue%20is%3Aopen%20milestone%3A%22KubeCon%20NA%202026%20ContribFest%2C%202026-11-11%22%20label%3Aevent%3Acontribfest%20label%3Astatus%3Aready%20no%3Aassignee).
Each Issue states its language, dependencies and checks. The same claim rules
apply to every task.

To request a task, comment on its Issue:

> I'd like to take this. GitHub: @yourname. Proposed branch:
> `issue-N-short-slug`.

A facilitator records your ownership and changes the label to
`status:in-progress`. You can then create the branch in your fork. You do not
need label or assignment permissions. Follow the
[claim guide](../../CONTRIBFEST.md#2-claim-one-issue) for sign-off and review.

<a id="choose-your-level"></a>

## Choose your level

Choose a topic you want to learn, then check the skills and setup it needs.
These levels describe the change, not your ability or a promised completion
time. A coding agent is optional at every level.

- **Beginner:** a focused test, status field or input check, with a small edit
  surface. Basic familiarity with the issue's programming language helps.
- **Intermediate:** coordinate retries, review decisions, CI or state across
  several functions, and check their failure paths.
- **Advanced:** reason about persistent writes, replay, recovery or state
  across several steps or Runs.

The tables group the prepared tasks reviewed on November 5. They do not
reserve a task or replace its live approval and claim record. Open the issue
before choosing it, and check the approved-task filters above. A task may be
claimed after this list was written. Follow its exact **Before you start**
and **Check your work** instructions; setup and difficulty are separate.

### Beginner

| Task | Why your contribution helps | Needs |
| --- | --- | --- |
| [#34: Align Ticket Routing tests with the declared Go 1.23 version](https://github.com/cadence-workflow/cadence-ai-samples/issues/34) | Contributors using the documented Go version can compile and run the example tests. | Go 1.23 and a newer Go toolchain |
| [#112: Fix the Incident Triage clean-copy check](https://github.com/cadence-workflow/cadence-ai-samples/issues/112) | Someone copying Incident Triage into their own project can run its standalone checks. | Python; clean-copy setup downloads packages |
| [#121: Test that a lost reply does not save the conclusion twice](https://github.com/cadence-workflow/cadence-ai-samples/issues/121) | Your test will catch a future change that saves the same report twice after a retry. | Python only |
| [#126: Show the selected agent and booking receipts in status](https://github.com/cadence-workflow/cadence-ai-samples/issues/126) | Someone watching a trip can see who handled it and which bookings have actually completed. | Python only |
| [#133: Print a summary of work repeated after restart](https://github.com/cadence-workflow/cadence-ai-samples/issues/133) | A comparison run becomes easy to check automatically while keeping its existing readable table and evidence. | Python, Cadence; scripted comparison |
| [#136: Reject research plans that exceed the limits](https://github.com/cadence-workflow/cadence-ai-samples/issues/136) | A research request is either accepted intact or rejected clearly, rather than changed without the user knowing. | Python only |
| [#139: Add a low-confidence mock ticket example](https://github.com/cadence-workflow/cadence-ai-samples/issues/139) | Attendees can try the low-confidence routing decision without downloading or calling a model. | Go 1.24+; no model for focused tests |
| [#165: Make the Human in the Loop tests run in a copied recipe](https://github.com/cadence-workflow/cadence-ai-samples/issues/165) | Someone copying Human in the Loop into another project can still run its meaningful offline checks. | Python; copied setup downloads packages |

### Intermediate

| Task | Why your contribution helps | Needs |
| --- | --- | --- |
| [#71: Add Java 17 profile tests to pull-request CI](https://github.com/cadence-workflow/cadence-ai-samples/issues/71) | A broken generated Java scaffold is caught before it reaches contributors. | Java 17, Gradle, CI configuration |
| [#110: Test that revision reuses evidence and guidance collects more](https://github.com/cadence-workflow/cadence-ai-samples/issues/110) | A future revision change cannot silently start extra lookups, or lose the reviewer request when investigation resumes. | Python only |
| [#111: Demonstrate recovery from a rate-limited model call](https://github.com/cadence-workflow/cadence-ai-samples/issues/111) | Participants can see model-call recovery, rather than only a tool-call retry. | Python, Cadence, Ollama/Qwen |
| [#120: Demonstrate expiration of an unanswered triage approval](https://github.com/cadence-workflow/cadence-ai-samples/issues/120) | Participants can demonstrate what happens when a reviewer never responds, instead of assuming the wait is bounded. | Python, Cadence, Ollama/Qwen |
| [#122: Stop retrying invalid booking input](https://github.com/cadence-workflow/cadence-ai-samples/issues/122) | An empty city or address stops promptly instead of consuming attempts that cannot repair it. | Python; Cadence for retry evidence |
| [#124: Set an explicit limit on agent turns](https://github.com/cadence-workflow/cadence-ai-samples/issues/124) | The recipe states its own eight-turn limit and explains exhaustion instead of relying on an inherited SDK default. | Python only |
| [#125: Test recovery and exhaustion for booking retries](https://github.com/cadence-workflow/cadence-ai-samples/issues/125) | The OpenAI Agents recipe gains reproducible evidence for both bounded retry outcomes already checked by the ADK version. | Python, Cadence; mock Worker |
| [#127: Retry temporary ride-booking failures](https://github.com/cadence-workflow/cadence-ai-samples/issues/127) | An approved ride has a clear recovery budget when booking fails temporarily, without retrying an invalid request. | Python; Cadence for retry evidence |
| [#128: Expire unanswered ride approvals](https://github.com/cadence-workflow/cadence-ai-samples/issues/128) | A ride proposal ends with a clear expiry outcome when nobody responds. | Python; Cadence for timer history |
| [#130: Limit repeated approval rounds](https://github.com/cadence-workflow/cadence-ai-samples/issues/130) | Repeated ride proposals cannot keep asking a reviewer indefinitely. | Python only |
| [#131: Show whether a ride approval was applied](https://github.com/cadence-workflow/cadence-ai-samples/issues/131) | A reviewer can tell why an approval was ignored rather than wondering why the ride still waits. | Python only |
| [#134: Expire unanswered research reviews](https://github.com/cadence-workflow/cadence-ai-samples/issues/134) | An unanswered research report expires explicitly and remains unpublished. | Python; Cadence for timer history |
| [#135: Stop retrying invalid research sources](https://github.com/cadence-workflow/cadence-ai-samples/issues/135) | The research agent stops wasting attempts on a source URL the reader cannot accept. | Python; Cadence for retry evidence |
| [#137: Test early, invalid and duplicate research decisions](https://github.com/cadence-workflow/cadence-ai-samples/issues/137) | Existing protections against invalid or duplicate review decisions become regression-tested in the OpenAI Agents recipe. | Python only |
| [#138: Stop retrying invalid mock tickets](https://github.com/cadence-workflow/cadence-ai-samples/issues/138) | Mock mode teaches the same permanent-versus-temporary failure rule as the live classifier. | Go 1.24+; no model |

### Advanced

| Task | Why your contribution helps | Needs |
| --- | --- | --- |
| [#123: Prevent duplicate bookings after a lost reply](https://github.com/cadence-workflow/cadence-ai-samples/issues/123) | Retrying one booking request can recover its receipt without creating a duplicate or confusing separate trip legs. | Python, local SQLite |
| [#129: Prevent duplicate rides after a lost booking reply](https://github.com/cadence-workflow/cadence-ai-samples/issues/129) | A confirmed ride can return its original receipt after a lost reply instead of booking another ride. | Python, local SQLite |
| [#132: Check that triage claims quote collected evidence](https://github.com/cadence-workflow/cadence-ai-samples/issues/132) | Reviewers can see invented, altered or misattributed quotations before deciding whether to accept a report. | Python; see issue for model-output checks |
| [#140: Show the ticket acknowledgment deadline in parent status](https://github.com/cadence-workflow/cadence-ai-samples/issues/140) | Someone inspecting the parent can see when the actual acknowledgment wait expires without a drifting second deadline. | Go 1.24+, Cadence histories |
| [#141: Replay ticket acknowledgment and timeout histories](https://github.com/cadence-workflow/cadence-ai-samples/issues/141) | Changes to routed-ticket code can be checked against histories that include the acknowledgment and expiry paths. | Go 1.24+, Cadence histories |
| [#142: Skip a release after repeated processing failures](https://github.com/cadence-workflow/cadence-ai-samples/issues/142) | One broken release no longer blocks the watch from processing every later update. | Python only |
| [#164: Rewind an agent investigation with Workflow Reset](https://github.com/cadence-workflow/cadence-ai-samples/issues/164) | Participants can practice rerunning a bad investigation branch while keeping earlier recorded evidence. | Python, Cadence; scripted model |

**Python only** means the core unit checks need no Cadence server or model.
Install the dependencies first. Some tests use a local HTTP fixture, so keep
localhost available when testing without external connectivity. The issue
states any additional runtime checks needed for its full contribution.

Ticket Routing tasks other than #34 use Go 1.24 or newer while the declared
Go 1.23 test-compatibility fix remains open. That avoids making your task
depend on another attendee's unfinished contribution.

**On hold:** [#109](https://github.com/cadence-workflow/cadence-ai-samples/issues/109)
is excluded while its quotation-quality checks do not pass.
[#143](https://github.com/cadence-workflow/cadence-ai-samples/issues/143),
[#144](https://github.com/cadence-workflow/cadence-ai-samples/issues/144) and
[#145](https://github.com/cadence-workflow/cadence-ai-samples/issues/145) have
existing contribution ownership; do not start competing work.

### Recipe tasks

Browse the [full attendee issue pool in Get started](README.md#issue-pool).
It lists the prepared tasks for every recipe and links to each Issue's
requirements. Check the approved tasks above for current availability before
requesting a claim.

## Extend the exercise

Each scenario in the Incident Triage recipe's
[`run_exercise.py`](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/run_exercise.py)
pairs a prepared failure with checks of the Workflow's behavior. To add one,
for example an approval that never arrives
([durable timers](https://cadenceworkflow.io/docs/concepts/timers/)) or a write
whose reply is lost
([Activity execution](https://cadenceworkflow.io/docs/concepts/activities/)), copy the `rate-limit` scenario, change the
failure, and write its checks. Open an Issue describing it before the pull
request.

## Bring your own workflow

Start from [#118](https://github.com/cadence-workflow/cadence-ai-samples/issues/118). Open your own Issue titled
`<Example> Make <your agent> durable`, so it can be claimed, reviewed and
continued by someone else.

Bring a small agent or script that's safe to share and makes at least one
model or tool call. Work through as many depths as you have time for:

1. **Wrap.** Start a Workflow that runs your agent in one Activity and returns
   its output. Run it and find it in Cadence Web.
2. **Break it.** Pick the call most likely to fail (a rate-limited API, a slow
   model, a flaky tool). Make it fail on purpose and watch what happens.
3. **Make it durable.** Move that call into its own Activity with a retry
   policy and a timeout. Read the retry guides for
   [Python](https://cadenceworkflow.io/docs/python-client/retries/) or
   [Go](https://cadenceworkflow.io/docs/go-client/retries/), then mark permanent
   errors as non-retryable.
4. **Steer (stretch).** Add a [Signal](https://cadenceworkflow.io/docs/python-client/signals/) so a person approves before the agent
   acts.

The [Incident Triage recipe](../../recipes/incident-triage/python/bare/workflow.py)
shows every step: model and tool calls as Activities, retry policies,
non-retryable errors and review Signals. Copy from it.

If you don't finish, write down the commands, what works and the next step,
and open an Issue so someone can continue.

## Explore and file what you find

[#119](https://github.com/cadence-workflow/cadence-ai-samples/issues/119): run Incident Triage in mock mode, stop the worker mid-run,
send Signals, run two at once. Open a `<Finding>` Issue for anything that
surprised you. No model needed.

**If you'd rather click than type (optional):** from the repository root, run
`./scripts/explore.sh`. Choose Incident Triage, python, and mock mode (this
recipe has no framework selector).

1. **Refresh and check services**, then copy the Worker and start commands into
   separate terminals and run them.
2. **Resolve latest run** to find your Run.
3. Follow the [recipe walkthrough](../../recipes/incident-triage/README.md) to
   send guidance, a revision and approval: enter the field, select **Send …**,
   then **Confirm …**.
4. **Open history** to see the recorded Activities and Signals in Cadence Web.

The Explorer is a helper for navigation and controls; the terminal path above
works on its own. More details are in [setup](setup.md#optional-explore-the-samples-in-your-browser).

## Leave a useful result

Follow the [finish or hand off instructions](../../CONTRIBFEST.md#4-finish-or-hand-off).
