# Set up your laptop

Download the dependencies before the session so you can spend the time working
with the model and Cadence. The selected recipe's README is authoritative for
versions, services and commands. Prepare only what your task needs.

Everyone starts with the same Incident Triage exercise. It needs Python 3.12
or 3.13, local Cadence in domain `cadence-ai-samples` (see the
[Cadence requirements](../../recipes/ticket-routing/README.md#requirements)),
and [Ollama](https://ollama.com/download) with `qwen2.5:7b`. The model is a
4.7 GB download and used 5.1 GB of memory when loaded in our test:

```bash
ollama pull qwen2.5:7b
```

A coding agent is separate from the model used by the running example.

## Get the code and check setup

Fork and clone [cadence-ai-samples](https://github.com/cadence-workflow/cadence-ai-samples)
using the [contributor instructions](../../CONTRIBUTING.md#first-time-contributor-path).
From your checkout's root:

```bash
cd recipes/incident-triage/python/bare
./run.sh setup
.venv/bin/python -m unittest discover -s tests -v
```

The tests use fixtures. Passing them checks the code setup; it does not mean
you have called a real model. Keep installation and model download separate
from the time needed to run an already prepared example.

## Check that a real model answers

With Cadence and Ollama running, from the same recipe directory:

```bash
.venv/bin/python exercises/retry_policy_live/run_exercise.py --scenario baseline
```

The run is working when you see:

- `MODEL RESPONSE` lines with the lookups the model chose, each after a
  `SPEND` line with the input and output tokens the model reported;
- the Workflow ID, Run ID and a Cadence Web link you can open;
- a draft report waiting for review. Type `reject` to finish.

`SETUP FAILED` names the missing piece. A model error prints
`MODEL CALL FAILED` and the run ends `FAILED`; there is no scripted answer.
Keep that output and show a helper.

`--model-id` picks another entry from the repository's
[`models.yaml`](../../models.yaml). `llama3.2-local` is smaller but often
drafts the wrong cause. Paid providers need `MODEL_AI_KEY`.

## The introductory retry exercise

Follow the [exercise README](../../recipes/incident-triage/python/bare/exercises/retry_policy_live/README.md).
You edit one file to make a temporary 429 recover and a permanent 404 stop,
then see the repeated-call guard and how `revise` and `guidance` differ.

## If setup or internet access fails

Tell a helper which command failed and keep its output. You can pair on a
working laptop if useful. Not every laptop can run the model.

A source archive does not contain installed Python packages, container images
or model weights. Download them before travel. Before relying on disconnected
work, try the whole selected task with networking disabled and localhost still
available. Claim upstream work while online; after reconnecting, confirm
ownership before pushing. A repeatable walkthrough needs no Issue claim.

Save commands, IDs, model receipts, changed files and the next step. Stop only
services and Workers you started. Use the [task list](shortlist.md) to choose
your next contribution.
