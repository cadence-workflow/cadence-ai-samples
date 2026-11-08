"""Measure one local controlled comparison, with owned processes and real inference.

Do not run while another recording needs the shared local model endpoint.
"""

from __future__ import annotations

import argparse
import asyncio
import collections
import hashlib
import json
import os
import queue
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "source"
sys.path.insert(0, str(SOURCE))
import cadence
from cadence.api.v1.common_pb2 import WorkflowExecution
from cadence.api.v1.service_workflow_pb2 import (
    DescribeWorkflowExecutionRequest,
    GetWorkflowExecutionHistoryRequest,
    TerminateWorkflowExecutionRequest,
)
from cadence.contrib.pydantic import PydanticDataConverter
from google.protobuf.json_format import MessageToDict
import story
import workflow
from protocol import GUIDANCE, MAX_STEPS, REPEAT_LIMIT, REVIEW, SECOND_REVIEW


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def usage(state, phase=None):
    rows = read(state / "model-spend.jsonl")
    if phase is not None:
        rows = [row for row in rows if row.get("phase") == phase]
    totals = {}
    for name in ("input_tokens", "output_tokens"):
        values = [row.get(name) for row in rows]
        totals[name] = sum(values) if all(isinstance(x, int) for x in values) else None
    return {"calls": len(rows), **totals}


def stop(processes):
    for process in processes:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)


def spawn_worker(state, task_list, role, label, args):
    environment = {
        **os.environ,
        "INCIDENT_TRIAGE_STATE": str(state),
        "INCIDENT_TRIAGE_MODEL": "live",
        "INCIDENT_TRIAGE_MODEL_ID": os.environ.get("INCIDENT_TRIAGE_MODEL_ID", "qwen-local"),
        "INCIDENT_TRIAGE_CATALOG": os.environ.get("INCIDENT_TRIAGE_CATALOG", str(SOURCE / "models.yaml")),
        "TRIAGE_PHASE": "cadence",
    }
    with (state / (label + ".log")).open("w") as log:
        return subprocess.Popen([
            sys.executable, "-u", "worker.py", "--role", role, "--id", label,
            "--task-list", task_list, "--target", args.target, "--domain", args.domain,
        ], cwd=SOURCE, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)


async def capture_cadence(root, args):
    state = root / "cadence"
    state.mkdir()
    workflow_id = "paired-cadence-" + uuid.uuid4().hex[:10]
    task_list = "paired-cadence-" + uuid.uuid4().hex
    save(state / "faults.json", {workflow_id: {"logs": {"status": 429, "times": 1}}})
    client = cadence.Client(domain=args.domain, target=args.target, identity="paired-measurement", data_converter=PydanticDataConverter())
    workers = [spawn_worker(state, task_list, role, role + "-A", args) for role in ("workflow", "activity")]
    execution = None
    completed = False

    async def status():
        return await client.query_workflow(workflow_id, execution.run_id, workflow.STATUS_QUERY, result_type=dict)

    async def wait_for(predicate, label, timeout=360):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = await status()
            if predicate(value):
                return value
            if value.get("phase") == "DONE":
                raise RuntimeError(f"Cadence ended before {label}: {value.get('outcome')}")
            await asyncio.sleep(0.15)
        raise TimeoutError(label)

    async def events():
        result, token = [], b""
        while True:
            response = await client.workflow_stub.GetWorkflowExecutionHistory(GetWorkflowExecutionHistoryRequest(domain=args.domain, workflow_execution=WorkflowExecution(workflow_id=workflow_id, run_id=execution.run_id), next_page_token=token, page_size=1000))
            result.extend(MessageToDict(event, preserving_proto_field_name=True) for event in response.history.events)
            token = response.next_page_token
            if not token:
                return result

    try:
        execution = await client.start_workflow(workflow.WORKFLOW, workflow.RecipeInput(story.trace_text(), {
            "max_steps": MAX_STEPS, "repeat_limit": REPEAT_LIMIT,
            "inject_duplicate": True, "presentation_mode": False,
            "scan_seconds": 0.1, "rescan_seconds": 0.05,
            "approval_window_seconds": 3600,
        }), task_list=task_list, workflow_id=workflow_id, execution_start_to_close_timeout=timedelta(minutes=15), task_start_to_close_timeout=timedelta(seconds=10))
        first = await wait_for(lambda x: x["phase"] == "AWAITING_GUIDANCE", "first draft")
        save(state / "first-draft.json", first)
        assert first["injected_proposal"].get("model_generated") is False
        assert first["injected_proposal"].get("executed") is False
        await client.signal_workflow(workflow_id, execution.run_id, workflow.REVISE_SIGNAL, REVIEW)
        revised = await wait_for(lambda x: x["phase"] == "AWAITING_GUIDANCE" and x["revision"] == 1, "explicit revision")
        save(state / "revised-draft.json", revised)
        await client.signal_workflow(workflow_id, execution.run_id, workflow.GUIDANCE_SIGNAL, GUIDANCE)
        approval = await wait_for(lambda x: x["phase"] == "AWAITING_APPROVAL", "approval checkpoint")
        save(state / "guided-draft-before-second-review.json", approval)
        await client.signal_workflow(workflow_id, execution.run_id, workflow.REVISE_SIGNAL, SECOND_REVIEW)
        approval = await wait_for(lambda x: x["phase"] == "AWAITING_APPROVAL" and x["revision"] == 2, "second explicit human revision")
        save(state / "approval-before-worker-loss.json", approval)
        before = usage(state)
        save(state / "usage-before-worker-loss.json", before)
        stop(workers)
        workers = []
        print("CADENCE_OUTAGE: both owned Workers stopped at approval.", flush=True)
        await asyncio.sleep(1.5)
        down = usage(state)
        save(state / "usage-zero-workers.json", down)
        history_down = await events()
        save(state / "history-zero-workers.json", history_down)
        assert down == before, "Model usage changed with zero Workers"
        workers = [spawn_worker(state, task_list, role, role + "-B", args) for role in ("workflow", "activity")]
        restored = await wait_for(lambda x: x["phase"] == "AWAITING_APPROVAL", "restored approval checkpoint")
        after = usage(state)
        save(state / "approval-after-worker-loss.json", restored)
        save(state / "usage-after-worker-loss.json", after)
        assert before == after, "Worker replacement repeated inference"
        assert restored["conclusion"] == approval["conclusion"]
        assert restored["revision"] == approval["revision"] == 2
        await client.signal_workflow(workflow_id, execution.run_id, workflow.APPROVAL_SIGNAL, "approve")
        final = await wait_for(lambda x: x["phase"] == "DONE", "completed synthetic report")
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            history = await events()
            if any("workflow_execution_completed_event_attributes" in event for event in history):
                break
            await asyncio.sleep(0.1)
        else:
            raise TimeoutError("No server completion event")
        assert final["outcome"] == "conclusion_uploaded"
        completed = True
        save(state / "final-status.json", final)
        save(state / "history-final.json", history)
        assert usage(state) == before, "Approval unexpectedly called the model"
        metadata = {"workflow_id": workflow_id, "run_id": execution.run_id, "task_list": task_list, "service_status": "COMPLETED", "recovery_calls": after["calls"] - before["calls"], "outage_usage_before": before, "outage_usage_during": down, "outage_usage_after": after}
        save(state / "execution.json", metadata)
        return metadata
    finally:
        if execution is not None and not completed:
            try:
                await client.cancel_workflow(workflow_id, execution.run_id)

                async def wait_for_close(timeout):
                    deadline = time.monotonic() + timeout
                    while time.monotonic() < deadline:
                        response = await asyncio.wait_for(
                            client.workflow_stub.DescribeWorkflowExecution(
                                DescribeWorkflowExecutionRequest(
                                    domain=args.domain,
                                    workflow_execution=WorkflowExecution(
                                        workflow_id=workflow_id, run_id=execution.run_id,
                                    ),
                                )
                            ),
                            timeout=3,
                        )
                        info = response.workflow_execution_info
                        if info.HasField("close_time"):
                            save(state / "cleanup-terminal.json", MessageToDict(info, preserving_proto_field_name=True))
                            return True
                        await asyncio.sleep(0.2)
                    return False

                if not await wait_for_close(10):
                    # Only this failed measurement's unique execution is affected.
                    await client.workflow_stub.TerminateWorkflowExecution(
                        TerminateWorkflowExecutionRequest(
                            domain=args.domain,
                            workflow_execution=WorkflowExecution(
                                workflow_id=workflow_id, run_id=execution.run_id,
                            ),
                            reason="Aborted local paired measurement; bounded cancellation did not close it",
                            identity="paired-measurement-cleanup",
                        )
                    )
                    if not await wait_for_close(5):
                        raise TimeoutError("Owned measurement execution did not close after termination")
            except Exception as error:
                save(state / "cleanup-error.json", {"error": str(error)})
        stop(workers)
        await client.close()


def capture_raw(root):
    state = root / "raw"
    state.mkdir()
    save(state / "external-fault.json", {"remaining": 1})
    run_id = "paired-raw-" + uuid.uuid4().hex[:10]
    transcript = (state / "console.log").open("w")
    processes = []
    try:
        for phase in ("first", "restart"):
            command = [sys.executable, "-u", str(HERE / "raw_runner.py"), "--state", str(state), "--phase", phase, "--run-id", run_id]
            if phase == "restart":
                command.append("--approve")
            process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
            processes.append(process)

            output = queue.Queue()

            def collect_lines(stream, inbox):
                try:
                    for line in stream:
                        inbox.put(line)
                finally:
                    inbox.put(None)

            threading.Thread(target=collect_lines, args=(process.stdout, output), daemon=True).start()
            reached = False
            deadline = time.monotonic() + 1200
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Raw {phase} exceeded the 20-minute controller deadline")
                try:
                    line = output.get(timeout=1)
                except queue.Empty:
                    continue
                if line is None:
                    break
                transcript.write(line)
                transcript.flush()
                print(line, end="", flush=True)
                if line.startswith("RAW_READY_FOR_APPROVAL"):
                    reached = True
                    if phase == "first":
                        before = usage(state)
                        save(state / "usage-before-process-loss.json", before)
                        stop([process])
                        print("RAW_OUTAGE: owned uncheckpointed process killed at approval.", flush=True)
                        break
            if not reached:
                raise RuntimeError(f"Raw {phase} failed before approval; code={process.wait()}")
            if phase == "restart" and process.wait() != 0:
                raise RuntimeError("Raw restart failed")
        metadata = {"run_id": run_id, "recovery_calls": usage(state, "restart")["calls"], "first": usage(state, "first"), "restart": usage(state, "restart"), "service_status": "local process completed", "fault_scope": "one429 consumed once overall; duplicate injection repeats in each restarted initial investigation because its execution flag was in memory"}
        save(state / "execution.json", metadata)
        return metadata
    finally:
        stop(processes)
        transcript.close()


def metrics(state):
    ledger = read(state / "ledger.jsonl")
    counts = collections.Counter(row["tool"] for row in ledger)
    gateway_successes = sum(row["tool"] == "get_logs_by_trace_id" and row.get("service") == "api-gateway" and row.get("status") == 200 for row in ledger)
    setup_repeated = sum(max(0, counts[name] - 1) for name in ("identify_input_params", "store_trace", "fetch_dependency_graph")) + max(0, gateway_successes - 1)
    writes = sum(row["tool"] == "upload_conclusion" and row.get("committed") is True for row in ledger)
    with sqlite3.connect(state / "store.db") as database:
        rows = database.execute("select count(*) from conclusions").fetchone()[0]
    assert writes == rows == 1
    received = len(read(state / "model-responses.jsonl"))
    model_attempts = counts["plan_next"] + counts["revise_draft"]
    assert len(read(state / "model-spend.jsonl")) == received, "Each actual model response must have a usage receipt"
    assert model_attempts == received, "A model invocation has no response receipt; usage accounting is incomplete"
    return {**usage(state), "model_invocations": model_attempts, "response_receipts": received, "invocations_without_response_receipt": model_attempts - received, "setup_repeated": setup_repeated, "writes": writes, "database_report_rows": rows, "ledger_counts": dict(counts)}


def request_equivalence(cadence_state, raw_state):
    cadence_requests = [row["request"] for row in read(cadence_state / "model-responses.jsonl")]
    raw_requests = read(raw_state / "model-responses.jsonl")
    first_count = usage(raw_state, "first")["calls"]
    first = [row["request"] for row in raw_requests[:first_count]]
    restart = [row["request"] for row in raw_requests[first_count:]]

    def first_mismatch(left, right):
        for index in range(max(len(left), len(right))):
            if index >= len(left) or index >= len(right) or left[index] != right[index]:
                return index + 1
        return None

    return {"cadence_and_raw_first_exact_request_bodies_equal": cadence_requests == first, "raw_first_and_restart_exact_request_bodies_equal": first == restart, "cadence_raw_first_mismatch_at_response": first_mismatch(cadence_requests, first), "raw_first_restart_mismatch_at_response": first_mismatch(first, restart), "cadence_response_count": len(cadence_requests), "raw_first_response_count": len(first), "raw_restart_response_count": len(restart), "note": "Protocol/configuration are fixed; exact equality is checked, not assumed. A mismatch limits causal token comparisons; each path's actual recovery usage remains separately observed."}


def priced_estimate(counts, input_rate, output_rate):
    if input_rate is None or output_rate is None:
        return None
    if counts["input_tokens"] is None or counts["output_tokens"] is None:
        return None
    result = (Decimal(counts["input_tokens"]) * input_rate + Decimal(counts["output_tokens"]) * output_rate) / Decimal(1000000)
    return str(result)


async def run(args):
    root = args.evidence.resolve()
    root.mkdir(parents=True, exist_ok=False)
    expected = json.loads((HERE / "source-provenance.json").read_text())["files_sha256"]
    assert all(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest for name, digest in expected.items()), "Frozen source changed"
    cadence_meta = await capture_cadence(root, args)
    raw_meta = capture_raw(root)
    cadence_counts = metrics(root / "cadence")
    raw_counts = metrics(root / "raw")
    cadence_counts["recovery_calls"] = cadence_meta["recovery_calls"]
    raw_counts["recovery_calls"] = raw_meta["recovery_calls"]
    assert cadence_counts["calls"] > 0 and raw_counts["calls"] > 0
    assert all(isinstance(x[name], int) and x[name] > 0 for x in (cadence_counts, raw_counts) for name in ("input_tokens", "output_tokens")), "Actual usage required"
    rates = {"input_usd_per_million": str(args.input_rate) if args.input_rate is not None else None, "output_usd_per_million": str(args.output_rate) if args.output_rate is not None else None}
    result = {
        "scope": "One controlled local comparison against this uncheckpointed restart baseline; not all plain Python designs.",
        "model": "qwen2.5:7b",
        "raw": raw_counts,
        "cadence": cadence_counts,
        "cadence_execution": cadence_meta,
        "raw_execution": raw_meta,
        "request_equivalence": request_equivalence(root / "cadence", root / "raw"),
        "operator_protocol": {"first_explicit_review": REVIEW, "guidance": GUIDANCE, "second_explicit_review": SECOND_REVIEW, "past_review_reapplied_after_guidance": False},
        "optional_rate_inputs": rates,
        "hypothetical_token_priced_usd": {"raw": priced_estimate(raw_counts, args.input_rate, args.output_rate), "cadence": priced_estimate(cadence_counts, args.input_rate, args.output_rate)},
        "actual_external_model_api_charge_usd": 0,
        "local_compute_usd": None,
        "cadence_infrastructure_usd": None,
        "limitations": ["Actual provider-reported logical tokens, including possible cached prompt context", "No hardware-energy or infrastructure prices measured", "One recorded example, not a production benchmark", "Synthetic incidents/tools/faults; model diagnosis not certified", "Raw input/report side-effect storage is durable, but execution/checkpoint state is not", "Raw restarts from input and replays explicit operator messages; a checkpointed Python design would have different behavior"],
    }
    save(root / "comparison.json", result)
    print("OBSERVED COMPARISON", flush=True)
    for title, key in (("Model responses", "calls"), ("Input tokens", "input_tokens"), ("Output tokens", "output_tokens"), ("Responses after process/Worker loss", "recovery_calls"), ("Setup steps repeated", "setup_repeated"), ("Report writes", "writes")):
        print(f"{title}: raw={raw_counts[key]}, Cadence={cadence_counts[key]}", flush=True)
    print("Exact request equivalence: " + json.dumps(result["request_equivalence"]), flush=True)
    print("END: one keyed synthetic report per path; no production cost or correctness claim.", flush=True)


def rate(value):
    result = Decimal(value)
    if not result.is_finite() or result < 0:
        raise argparse.ArgumentTypeError("Rate must be a finite nonnegative number")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="localhost:27833")
    parser.add_argument("--domain", default="incident-demo")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--input-rate", type=rate)
    parser.add_argument("--output-rate", type=rate)
    asyncio.run(run(parser.parse_args()))
