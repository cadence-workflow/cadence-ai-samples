# Agent Handoffs

## Problem

Trip planning can require multiple specialists: a local ride for a short trip, or
a flight plus airport rides for a long trip. Delegation and completed bookings
must survive Worker restarts without repeating model or tool Activities.

## Solution

A coordinating trip planner hands off to short- or long-trip specialists using
either OpenAI Agents or Google ADK. Synthetic `book-flight` and `book-ride`
tools are Cadence Activities. Mock mode routes deterministically and never reads
catalogs or contacts a provider.

## Architecture

`request → mock route or live handoffs → synthetic booking Activities → result`

In live mode, the selected framework runs in Workflow code. Cadence turns each
provider request into `OpenAIActivities.invoke_model` or
`GoogleADKActivities.generate_content_async`; booking tools are separate
Activities. Google ADK uses a coordinator `LlmAgent`, specialist `sub_agents`,
and the built-in `transfer_to_agent` tool. The Worker resolves the Workflow's
logical model name to its selected `models.yaml` entry and rewrites a copy of
the request with the provider-specific runtime model immediately before
transport. The logical request in Workflow history remains unchanged.

## Requirements

- Python 3.12 or 3.13.
- A Cadence server at `localhost:7833` with domain `cadence-ai-samples`.
- Live mode only: a compatible entry in repository-root `models.yaml`.

Both implementations pin Cadence Python client commit
`2bc1af4207d20cd99ae64fa1ef82d803905af947` and Pydantic `2.12.5`. The OpenAI
implementation pins OpenAI Agents `0.12.5`; the Google ADK implementation pins
Google ADK `2.1.0` and LiteLLM `1.83.7`.

## Fresh-checkout setup

Choose one implementation from the repository root:

```bash
# OpenAI Agents
cd recipes/agent-handoffs/python/openai-agents
./run.sh setup
```

```bash
# Google ADK
cd recipes/agent-handoffs/python/google-adk
./run.sh setup
```

If your default package index requires unavailable credentials, use the public
index:

```bash
PIP_INDEX_URL=https://pypi.org/simple .venv/bin/python -m pip install -e .
```

## Offline mock walkthrough

From either implementation directory, start one mock Worker and keep it running:

```bash
./run.sh worker --mode mock
```

In another terminal, start a short local trip:

```bash
./run.sh --workflow-id handoffs-short start --mode mock \
  --text "Book a ride from 123 Market Street to 1 Ferry Building in San Francisco."
```

Start a long inter-city trip with a different Workflow ID:

```bash
./run.sh --workflow-id handoffs-long start --mode mock \
  --text "Book a trip for me from Uber Seattle Office to Uber San Francisco Office tomorrow at 10:00 AM."
```

Mock mode does not read `models.yaml`, inspect credentials, or call an AI or
booking provider.

## Live mode

Live mode runs the selected framework's native handoffs in Workflow code with
Activity-backed model and booking tools. Workflow code parses the request,
offers the coordinator only the matching specialist, and gives that specialist
booking tools that take no arguments: `book_ride` for a short trip and
`book_long_trip` for the flight and both airport rides. The model still makes
the framework handoff and the tool call, each booking is its own Activity, and
nothing is booked unless the model calls the tool. When small local models had
to choose the specialist and copy every booking detail, they routed wrongly and
invented details.

With local Ollama, the strict check below passed 5 of 5 runs for each model on
OpenAI Agents, and 5 of 5 for `llama3.2-local` on Google ADK. `qwen2.5-local`
on Google ADK passed 9 of 10; the failure was a model-call timeout while other
live jobs shared the CPU. These runs used CPU-only Ollama 0.40.13 on Linux.
Remote catalog entries are not yet proven
([Issue #47](https://github.com/cadence-workflow/cadence-ai-samples/issues/47)).
Google and OpenAI catalog entries require `MODEL_AI_KEY` and an HTTPS endpoint.

Example live Worker with a remote catalog entry (requires authorization and a
key):

```bash
export MODEL_AI_KEY="replace-with-your-key"
./run.sh worker --mode live --confirm-live --model-id gemini-flash-lite
```

In another terminal:

```bash
./run.sh start --mode live \
  --text "Book a trip from Uber Seattle Office to Uber San Francisco Office tomorrow at 10:00 AM."
```

Worker and start commands must use the same `--domain` and `--task-list`. The
start command has no catalog, model, endpoint, or credential options. The OpenAI
implementation sets an internal API-key compatibility shim for local Ollama.
The Google ADK implementation uses LiteLLM's loopback Ollama transport;
operators do not export a key for either local path.

## Workflow ID reuse

The default Workflow IDs are `agent-handoffs-openai-agents-demo` and
`agent-handoffs-google-adk-demo`, each with `ALLOW_DUPLICATE`. After a Run
closes, the same ID can start again. An open duplicate is rejected with a clear
error.

## Reliability and failures

Model Activities use a 30-second schedule-to-close timeout and up to three
attempts with exponential backoff. Synthetic booking Activities use the same
30-second timeout and three-attempt retry policy. Authentication, configuration,
and schema errors are non-retryable. Provider error bodies are not copied into
Activity failures.

## Tests

From either implementation directory:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Local Cadence mock durability (requires Cadence at `localhost:7833`):

```bash
python tests/local_cadence_checks.py
```

## Strict live capability check (optional)

`python tests/live_ollama_validation.py` runs live short and long requests for
the current implementation against `llama3.2-local` when Ollama serves it at
`localhost:11434` and Cadence is at `localhost:7833`. Pass `--model-id` to
select another local Ollama entry, for example `--model-id qwen2.5-local`. The
script **must exit non-zero** when the model omits required specialist handoffs
or booking tool Activities, and it prints the decoded failure message with the
retained Workflow and Run IDs. Google ADK also requires the actual
`transfer_to_agent` event and exact typed receipts.

The unit suites are fully offline except for the optional local scripts above.
The Google ADK suite drives the real `CadenceAgentRunner` and
`transfer_to_agent` machinery with controlled model Activity responses; it does
not replace the runner with a mock.

## Copying this recipe

Copy the entire `recipes/agent-handoffs` directory and keep provider clients and
model requests at Activity boundaries. Replace trip parsing, handoff instructions,
and synthetic booking fixtures for your domain.

## Manual setup recovery

If the launcher cannot prepare the implementation, run:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e .
```
