"""Uncheckpointed execution baseline; evidence files are not recovery state.

Input/report stores and one consumed external fault persist independently, as
ordinary tool side effects. This process never reads them to recover an agent's
execution position, decisions, prior draft or review state.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "source"))
import live_model
import story
from protocol import GUIDANCE, MAX_STEPS, REPEAT_LIMIT, REVIEW, SECOND_REVIEW


def record(state: Path, phase: str, tool: str, attempt: int = 0, **details):
    entry = {
        "tool": tool,
        "phase": phase,
        "attempt": attempt,
        "worker": f"raw-{os.getpid()}",
        "at": time.time(),
        **details,
    }
    with (state / "ledger.jsonl").open("a") as stream:
        stream.write(json.dumps(entry, sort_keys=True) + "\n")


async def run(args):
    state = args.state.resolve()
    state.mkdir(parents=True, exist_ok=True)
    os.environ["INCIDENT_TRIAGE_STATE"] = str(state)
    os.environ["INCIDENT_TRIAGE_MODEL"] = "live"
    os.environ.setdefault("INCIDENT_TRIAGE_MODEL_ID", "qwen-local")
    os.environ.setdefault("INCIDENT_TRIAGE_CATALOG", str(HERE.parent / "source/models.yaml"))
    os.environ["TRIAGE_PHASE"] = args.phase
    live_model.prepare()
    phase = args.phase

    async def logs(service, trace_id, prepared=False):
        for attempt in range(3):
            fault = state / "external-fault.json"
            remaining = json.loads(fault.read_text())["remaining"]
            if prepared and remaining:
                fault.write_text(json.dumps({"remaining": remaining - 1}))
                record(state, phase, "get_logs_by_trace_id", attempt, service=service, status=429)
                if attempt == 2:
                    raise RuntimeError("bounded gateway retries exhausted")
                await asyncio.sleep(10)
                continue
            result = story.logs_for(service, trace_id)
            record(state, phase, "get_logs_by_trace_id", attempt, service=service, status=200)
            return result
        raise RuntimeError("bounded gateway retries exhausted")

    async def model(call_name, function, *parameters):
        # Match the sample's bounded model-Activity retries, not a weaker baseline.
        async with asyncio.timeout(180):
            for attempt in range(3):
                record(state, phase, call_name, attempt)
                try:
                    return await asyncio.to_thread(function, *parameters)
                except (live_model.LiveConfigurationError, live_model.LiveAuthenticationError):
                    raise
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(10)

    params = story.identify_input_params(story.trace_text())
    record(state, phase, "identify_input_params")
    with sqlite3.connect(state / "store.db") as database:
        database.execute("create table if not exists traces (key text primary key, body text)")
        database.execute("insert or ignore into traces values (?, ?)", (args.run_id + "/input", json.dumps(params, sort_keys=True)))
    record(state, phase, "store_trace", key=args.run_id + "/input")
    gateway_task = asyncio.create_task(logs(params["service_name"], params["trace_id"], prepared=True))
    graph = story.dependency_graph()
    record(state, phase, "fetch_dependency_graph", status=200)
    gateway = await gateway_task
    start = graph["depth1"][0]

    async def investigate(guidance, inject_duplicate):
        hops, calls, repeats = [], [], {}
        guard = ""
        injected = False
        for step in range(1, MAX_STEPS + 1):
            action = await model("plan_next", live_model.plan, {
                "step": step,
                "start": start,
                "hops": hops,
                "guidance": guidance,
                "force_draft": bool(guard),
            })
            record(state, phase, "model_action", action=action, step=step, guidance=guidance)
            if action["tool"] == "draft":
                return {"conclusion": action["conclusion"], "hops": hops, "calls": calls, "guard": guard, "injected": injected}
            call = action["tool"] + json.dumps(action["args"], sort_keys=True)
            repeats[call] = repeats.get(call, 0) + 1
            if repeats[call] > REPEAT_LIMIT:
                guard = f"blocked repeated call {call}"
                record(state, phase, "duplicate_blocked", source="model", call=call, executed=False)
                continue
            calls.append(call)
            hops.append(await logs(action["args"]["service"], params["trace_id"]))
            if inject_duplicate and not injected and len(hops) == 2:
                injected = True
                guard = f"blocked injected duplicate {call} before dispatch"
                record(state, phase, "duplicate_blocked", source="deliberate fault injection after second successful tool lookup", model_generated=False, call=call, executed=False)
        raise RuntimeError("logical turn budget exhausted; no scripted answer fallback")

    initial = await investigate([], inject_duplicate=True)
    record(state, phase, "operator_revision", text=REVIEW)
    revised = await model("revise_draft", live_model.revise, initial["conclusion"], REVIEW, [gateway, *initial["hops"]])
    record(state, phase, "revision_complete", conclusion=revised)
    record(state, phase, "operator_guidance", text=GUIDANCE)
    final = await investigate([GUIDANCE], inject_duplicate=False)
    # Past revision requests are not silently replayed after guidance.
    record(state, phase, "operator_revision", text=SECOND_REVIEW)
    final["conclusion"] = await model(
        "revise_draft", live_model.revise,
        final["conclusion"], SECOND_REVIEW, [gateway, *final["hops"]],
    )
    record(state, phase, "second_revision_complete", conclusion=final["conclusion"])
    checkpoint = {
        "phase": "AWAITING_APPROVAL",
        "initial": initial,
        "revised": revised,
        "guided": final,
        "review": REVIEW,
        "second_explicit_review": SECOND_REVIEW,
        "guidance": GUIDANCE,
        "revision": 2,
        "execution_state": "in memory; no checkpoint loaded on restart",
    }
    (state / f"checkpoint-{phase}.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    record(state, phase, "awaiting_approval")
    print("RAW_READY_FOR_APPROVAL " + json.dumps({"phase": phase}), flush=True)
    if not args.approve:
        await asyncio.Event().wait()
    record(state, phase, "operator_approval", decision="approve", scope="synthetic local comparison only")
    key = args.run_id + "/conclusion"
    with sqlite3.connect(state / "store.db") as database:
        database.execute("create table if not exists conclusions (key text primary key, receipt text, body text)")
        previous = database.execute("select receipt from conclusions where key=?", (key,)).fetchone()
        if previous:
            receipt, committed = previous[0], False
        else:
            receipt, committed = "receipt-" + key.replace("/", "-"), True
            database.execute("insert into conclusions values (?, ?, ?)", (key, receipt, json.dumps(final["conclusion"], sort_keys=True)))
    record(state, phase, "upload_conclusion", key=key, committed=committed)
    print("RAW_COMPLETED " + json.dumps({"phase": phase, "receipt": receipt, "committed": committed}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--phase", choices=["first", "restart"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--approve", action="store_true")
    asyncio.run(run(parser.parse_args()))
