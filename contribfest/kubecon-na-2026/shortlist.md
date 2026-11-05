# Choose what to build

**Bring your own workflow to Cadence, or improve an example below.**

The [live GitHub issue pool](https://github.com/cadence-workflow/cadence-ai-samples/issues?q=is%3Aissue%20is%3Aopen%20label%3Aevent%3Acontribfest)
is the **official source**. Filter and sort it to find work, check current
status and see who has claimed it. The tables here are a November 5 snapshot
of prepared contributions, not the full pool or a limit on your ideas.

[Set up your checkout](setup.md) · [Bring your own workflow](#bring-your-own-workflow)

<a id="choose-a-contribfest-issue"></a>

## ContribFest Issues

1. Open an issue in the live pool. Choose work that is open, `status:ready`,
   unassigned and has no existing claim or active implementation PR.
2. Comment: **“I'd like to take this. GitHub: @yourname. Branch: `issue-N-short-slug`.”**
3. Wait for a facilitator to record your ownership and `status:in-progress`.
   Then create the branch in your fork and follow the issue's setup and checks.

You do not need label permissions. A facilitator records the claim for you. If a task is taken, choose another or propose your own.

<a id="choose-your-level"></a>

## Choose your level

Pick a topic you want to learn. Levels describe the change's complexity, not
your ability. You can work by hand or with an agent at any level.

### Beginner: focused edits

| What you will do | What you will learn | Setup |
| --- | --- | --- |
| [Run the tests on Go 1.23 · #34](https://github.com/cadence-workflow/cadence-ai-samples/issues/34) | Toolchain compatibility | Go 1.23 + newer |
| [Run Triage tests in a copied recipe · #112](https://github.com/cadence-workflow/cadence-ai-samples/issues/112) | Portable examples | Python |
| [Test a saved report with a lost reply · #121](https://github.com/cadence-workflow/cadence-ai-samples/issues/121) | Safe repeated writes | Python |
| [Show the trip agent and booking receipts · #126](https://github.com/cadence-workflow/cadence-ai-samples/issues/126) | Inspecting progress | Python |
| [Summarize work repeated after restart · #133](https://github.com/cadence-workflow/cadence-ai-samples/issues/133) | Recovering completed work | Python + Cadence |
| [Reject oversized research plans · #136](https://github.com/cadence-workflow/cadence-ai-samples/issues/136) | Clear input limits | Python |
| [Try an uncertain ticket in mock mode · #139](https://github.com/cadence-workflow/cadence-ai-samples/issues/139) | Handling low confidence | Go 1.24+ |
| [Run ride-agent tests in a copied recipe · #165](https://github.com/cadence-workflow/cadence-ai-samples/issues/165) | Portable examples | Python |

### Intermediate: connect behavior across steps

| What you will do | What you will learn | Setup |
| --- | --- | --- |
| [Test generated Java examples in CI · #71](https://github.com/cadence-workflow/cadence-ai-samples/issues/71) | Reproducible examples | Java 17 + Gradle |
| [Test revision and investigation decisions · #110](https://github.com/cadence-workflow/cadence-ai-samples/issues/110) | Reusing evidence | Python |
| [Demonstrate model rate-limit recovery · #111](https://github.com/cadence-workflow/cadence-ai-samples/issues/111) | Bounded retries | Python + Cadence + model |
| [Demonstrate an unanswered review · #120](https://github.com/cadence-workflow/cadence-ai-samples/issues/120) | Durable timers | Python + Cadence + model |
| [Stop retrying invalid booking input · #122](https://github.com/cadence-workflow/cadence-ai-samples/issues/122) | Permanent vs temporary errors | Python + Cadence |
| [Limit the agent to eight turns · #124](https://github.com/cadence-workflow/cadence-ai-samples/issues/124) | Bounded agent execution | Python |
| [Test booking recovery and exhaustion · #125](https://github.com/cadence-workflow/cadence-ai-samples/issues/125) | Retries and Worker restart | Python + Cadence |
| [Retry temporary ride-booking failures · #127](https://github.com/cadence-workflow/cadence-ai-samples/issues/127) | Retries after approval | Python + Cadence |
| [Expire unanswered ride approvals · #128](https://github.com/cadence-workflow/cadence-ai-samples/issues/128) | Durable timers | Python + Cadence |
| [Limit repeated approval rounds · #130](https://github.com/cadence-workflow/cadence-ai-samples/issues/130) | Bounded human review | Python |
| [Explain ignored ride approvals · #131](https://github.com/cadence-workflow/cadence-ai-samples/issues/131) | Inspecting review decisions | Python |
| [Expire unanswered research reviews · #134](https://github.com/cadence-workflow/cadence-ai-samples/issues/134) | Durable timers | Python + Cadence |
| [Stop retrying invalid research sources · #135](https://github.com/cadence-workflow/cadence-ai-samples/issues/135) | Permanent vs temporary errors | Python + Cadence |
| [Test early and repeated review decisions · #137](https://github.com/cadence-workflow/cadence-ai-samples/issues/137) | Signals and review state | Python |
| [Stop retrying invalid mock tickets · #138](https://github.com/cadence-workflow/cadence-ai-samples/issues/138) | Failure classification | Go 1.24+ |

### Advanced: state, replay and recovery

| What you will do | What you will learn | Setup |
| --- | --- | --- |
| [Prevent duplicate trip bookings · #123](https://github.com/cadence-workflow/cadence-ai-samples/issues/123) | Stable write keys | Python + SQLite |
| [Prevent duplicate ride bookings · #129](https://github.com/cadence-workflow/cadence-ai-samples/issues/129) | Stored booking receipts | Python + SQLite |
| [Check report quotations against logs · #132](https://github.com/cadence-workflow/cadence-ai-samples/issues/132) | Checking model claims | Python |
| [Show the ticket acknowledgment deadline · #140](https://github.com/cadence-workflow/cadence-ai-samples/issues/140) | Parent and child Workflows | Go 1.24+ + Cadence |
| [Replay acknowledged and expired tickets · #141](https://github.com/cadence-workflow/cadence-ai-samples/issues/141) | History compatibility | Go 1.24+ + Cadence |
| [Skip a repeatedly failing release · #142](https://github.com/cadence-workflow/cadence-ai-samples/issues/142) | Progress across Runs | Python |
| [Rewind an investigation with Reset · #164](https://github.com/cadence-workflow/cadence-ai-samples/issues/164) | Reusing recorded results | Python + Cadence |

**Setup notes:** Python tasks use 3.12 or 3.13. “Python” alone means the core
checks need no Cadence service or model. Install dependencies first; keep
localhost available for test fixtures. Each issue gives the full requirements.
Other Go tasks use 1.24+ while #34's compatibility fix remains open. #109 is
held while its quotation-quality checks fail; existing claims remain reserved.

### Recipe tasks

Use the live pool above to filter by recipe or sort by your interests. Check
availability there before starting any task from this snapshot.

## Bring your own workflow

**Build something useful to you and show how it recovers from one failure.**
Try a research assistant that resumes after a Worker stops, a travel agent
that waits for approval, or a coding agent that keeps completed tool results.
Invent your own example; use public or synthetic data.

1. [Open a Recipe proposal](https://github.com/cadence-workflow/cadence-ai-samples/issues/new?template=recipe-proposal.yml).
   Describe your agent, one failure, the expected recovery and how to test it
   without paid model access. Give a small first scope and an intended
   `recipes/<your-slug>/SPEC.md` path; the form guides the remaining fields.
2. Mention ContribFest and link invitation #118 in your description. Ask a
   facilitator to review it. Wait for approval as `status:ready` and a recorded
   claim as `status:in-progress` before upstream implementation.
3. Build and test your example in your fork. Record the setup, deliberate
   failure, recovery, Workflow/Run IDs and results. Keep progress and your
   draft PR on that issue so someone can continue if you stop.

Claim an existing issue when improving its task. Create a new proposal for
your own example. Do not duplicate a task or claim the umbrella invitation.

**A useful Cadence distinction:** a Workflow coordinates the job; Activities
perform calls such as asking a model or saving a report. Cadence records
completed Activity results. Put calls in separate Activities to give them
separate recovery points. Retrying a write can repeat its effect, so use a
stable request key when a repeated call must not save or book twice.

## Extend the exercise

Propose one new failure scenario using the Recipe form above. The
[retry exercise](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md)
is a starting point. Check the live pool first; a prepared task may already
cover your idea.

## Explore and file what you find

Run a sample in mock mode, stop your Worker, restart it and inspect what
survived. Use the [Explorer walkthrough](setup.md#optional-explore-the-samples-in-your-browser)
for controls and requirements. Record the steps and observations in a finding
through the repository's issue forms; #119 describes this exploration path.

## Leave a useful result

[Hand off your contribution](../../CONTRIBFEST.md#4-finish-or-hand-off) with
changed files, commands, results and the next step. A focused draft PR or a
clear unfinished handoff helps the next contributor.
