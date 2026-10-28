# Set up your laptop

Download the dependencies before the session so you can spend the time working
with the model and Cadence. The selected recipe's README is authoritative for
versions, services and commands. Prepare only what your task needs.

For the walkthrough, use the [Incident Triage README](../../recipes/incident-triage/README.md).
It documents Python 3.12 or 3.13, local Cadence in domain `cadence-ai-samples`,
and Ollama with `llama3.2:latest`. Use the linked
[Cadence requirements](../../recipes/ticket-routing/README.md#requirements)
and [model installation guide](../../README.md#install-ollama-and-llama32).
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

## Run the existing live example

With Cadence and Ollama available, start the Worker in one terminal:

```bash
./run.sh worker --mode live
```

In a second terminal, from the same recipe directory:

```bash
./run.sh start --mode live
```

Keep the printed Workflow ID and Run ID. A completed model call prints a
`SPEND` line with returned token usage. Missing usage stays unavailable.
If the model fails, keep that error rather than substituting a scripted answer.
The recipe's comparison command uses a scripted planner; it is a different
path and does not measure real-model tokens or cost.

Open the run in your local Cadence Web. Inspect the completed model and tool
Activities, then query the workflow's state. Read the draft beside the source
logs. Use the recipe's documented [Explorer controls](../../recipes/incident-triage/explorer.yaml)
for `revise`, `guidance` and `approval`; their inputs are strings.

You can end the initial review without saving a report by sending `reject`
through `approval`. To continue the investigation, follow the recipe's guidance
and review flow. Send `approve` only when the final report is ready. Record the
state and result after each action; receiving a Signal is separate from applying it.

## If setup or internet access fails

Tell a helper which command failed and keep its output. Ask about pairing or a
task with fewer prerequisites. Do not assume every laptop can run the model.

A source archive does not contain installed Python packages, container images
or model weights. Download them before travel. Before relying on disconnected
work, try the whole selected task with networking disabled and localhost still
available. Claim upstream work while online; after reconnecting, confirm
ownership before pushing. A repeatable walkthrough needs no Issue claim.

Save commands, IDs, model receipts, changed files and the next step. Stop only
services and Workers you started. See the [task list](shortlist.md) when ready.
