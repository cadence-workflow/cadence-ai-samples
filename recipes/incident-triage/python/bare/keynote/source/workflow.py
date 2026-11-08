"""Durable orchestration for the synthetic checkout incident."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Awaitable

from cadence import workflow
from cadence.worker import Registry

from activities import (
    ACTIVITIES,
    GET_LOGS_ACTIVITY,
    GRAPH_ACTIVITY,
    IDENTIFY_ACTIVITY,
    PLAN_ACTIVITY,
    REVISE_ACTIVITY,
    STORE_TRACE_ACTIVITY,
    UPLOAD_ACTIVITY,
)


WORKFLOW = "IncidentTriageWorkflow"
STATUS_QUERY = "status"
GUIDANCE_SIGNAL = "guidance"
REVISE_SIGNAL = "revise"
APPROVAL_SIGNAL = "approval"

QUICK_ACTIVITY = {
    "schedule_to_close_timeout": timedelta(seconds=600),
    "retry_policy": {
        "initial_interval": timedelta(seconds=10),
        "backoff_coefficient": 2.0,
        "maximum_interval": timedelta(seconds=10),
        "maximum_attempts": 3,
        "non_retryable_error_reasons": [
            "NonRetryableHttpError",
            "LiveConfigurationError",
            "LiveAuthenticationError",
        ],
    },
}
MODEL_ACTIVITY = {
    **QUICK_ACTIVITY,
    "schedule_to_close_timeout": timedelta(seconds=600),
}
SCAN_ACTIVITY = {
    **QUICK_ACTIVITY,
    "schedule_to_close_timeout": timedelta(minutes=10),
    "heartbeat_timeout": timedelta(seconds=5),
}


@dataclass(frozen=True)
class RecipeInput:
    text: str
    limits: dict[str, Any] = field(default_factory=dict)


class IncidentTriageWorkflow:
    """Follow one failing request, incorporate review, and wait durably."""

    def __init__(self) -> None:
        self.phase = "STARTING"
        self.last_model_action = {}
        self.injected_proposal = {}
        self.duplicate_injected = False
        self.inject_duplicate = False
        self.evidence = []
        self.presentation_mode = False
        self.presentation_checkpoint = ""
        self.presentation_releases = set()
        self.presentation_gate_count = 0
        self.params: dict[str, Any] = {}
        self.stored_path = ""
        self.lookups: dict[str, dict[str, str]] = {
            "gateway logs": {"status": "waiting", "result": ""},
            "dependency graph": {"status": "waiting", "result": ""},
        }
        self.calls: list[str] = []
        self.hops: list[dict[str, Any]] = []
        self.guidance_notes: list[str] = []
        self.pending_revisions: list[str] = []
        self.review_requests: list[str] = []
        self.conclusion: dict[str, Any] = {}
        self.decision = ""
        self.outcome = ""
        self.guard = ""
        self.hypothesis = ""
        self.revision = 0
        self.approval_window_seconds = 0.0

    @workflow.signal(name="presentation_continue")
    def presentation_continue(self, checkpoint: str) -> None:
        self.presentation_releases.add(checkpoint)

    async def presentation_gate(self, checkpoint: str) -> None:
        if self.presentation_mode:
            self.presentation_gate_count += 1
            checkpoint = f"{self.presentation_gate_count}:{checkpoint}"
            self.presentation_checkpoint = checkpoint
            await workflow.wait_condition(lambda: checkpoint in self.presentation_releases)
            self.presentation_checkpoint = ""

    @workflow.signal(name=GUIDANCE_SIGNAL)
    def add_guidance(self, text: str) -> None:
        self.guidance_notes.append(text)

    @workflow.signal(name=REVISE_SIGNAL)
    def revise(self, request: str) -> None:
        self.review_requests.append(request)
        self.pending_revisions.append(request)

    @workflow.signal(name=APPROVAL_SIGNAL)
    def approval(self, decision: str) -> None:
        self.decision = decision

    @workflow.query(name=STATUS_QUERY)
    def status(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "last_model_action": self.last_model_action,
            "injected_proposal": self.injected_proposal,
            "evidence": self.evidence,
            "presentation_checkpoint": self.presentation_checkpoint,
            "params": self.params,
            "stored_path": self.stored_path,
            "lookups": self.lookups,
            "calls": self.calls,
            "hops": [hop["service"] for hop in self.hops],
            "guidance": self.guidance_notes,
            "review_requests": self.review_requests,
            "guard": self.guard,
            "hypothesis": self.hypothesis,
            "revision": self.revision,
            "conclusion": self.conclusion,
            "decision": self.decision,
            "outcome": self.outcome,
            "approval_window_seconds": self.approval_window_seconds,
        }

    async def lookup(
        self, name: str, operation: Awaitable[dict[str, Any]]
    ) -> dict[str, Any] | None:
        self.lookups[name] = {"status": "running", "result": ""}
        try:
            result = await operation
        except Exception as error:
            self.lookups[name] = {
                "status": f"failed: {type(error).__name__}",
                "result": "",
            }
            return None
        self.lookups[name]["status"] = "done"
        return result

    def finish(self, outcome: str, **details: Any) -> dict[str, Any]:
        self.phase = "DONE"
        self.outcome = outcome
        return {
            "outcome": outcome,
            "conclusion": self.conclusion,
            "revision": self.revision,
            **details,
        }

    async def run_agent(
        self,
        start: str,
        trace_id: str,
        max_steps: int,
        repeat_limit: int,
    ) -> str | None:
        repeats: dict[str, int] = {}
        action: dict[str, Any] = {}
        for step in range(1, max_steps + 1):
            self.phase = "PLANNING"
            action = await workflow.execute_activity(
                PLAN_ACTIVITY,
                dict,
                {
                    "step": step,
                    "start": start,
                    "hops": self.hops,
                    "guidance": self.guidance_notes,
                    "force_draft": bool(self.guard),
                },
                **MODEL_ACTIVITY,
            )
            self.last_model_action = action
            self.hypothesis = action["hypothesis"]
            await self.presentation_gate("model_response")
            if action["tool"] == "draft":
                self.conclusion = action["conclusion"]
                return None
            call = action["tool"] + json.dumps(action["args"], sort_keys=True)
            repeats[call] = repeats.get(call, 0) + 1
            if repeats[call] > repeat_limit:
                self.guard = f"blocked repeated call {call}"
                continue
            self.phase = f"RUNNING {call}"
            self.calls.append(call)
            self.hops.append(
                await workflow.execute_activity(
                    GET_LOGS_ACTIVITY,
                    dict,
                    {
                        "service": action["args"]["service"],
                        "trace_id": trace_id,
                    },
                    **QUICK_ACTIVITY,
                )
            )
            self.evidence = list(self.hops)
            await self.presentation_gate("tool_result")
            if self.inject_duplicate and not self.duplicate_injected and len(self.hops) == 2:
                self.duplicate_injected = True
                self.injected_proposal = {
                    "tool": action["tool"], "args": action["args"],
                    "source": "deliberate fault injection after second successful tool lookup",
                    "model_generated": False,
                    "executed": False,
                }
                self.guard = f"blocked injected duplicate {call} before dispatch"
                await self.presentation_gate("duplicate_blocked")
        return "budget_exhausted"

    @workflow.run
    async def run(self, recipe_input: RecipeInput) -> dict[str, Any]:
        limits = {
            "max_steps": 10,
            "repeat_limit": 1,
            "approval_window_seconds": 3 * 24 * 60 * 60,
            "scan_seconds": 0.5,
            "rescan_seconds": 0.1,
            **recipe_input.limits,
        }
        self.presentation_mode = bool(limits.get("presentation_mode"))
        self.inject_duplicate = bool(limits.get("inject_duplicate"))
        self.approval_window_seconds = limits["approval_window_seconds"]
        info = workflow.WorkflowContext.get().info()
        workflow_id = info.workflow_id
        run_id = info.workflow_run_id

        await self.presentation_gate("workflow_started")
        self.phase = "READING INPUT"
        self.params = await workflow.execute_activity(
            IDENTIFY_ACTIVITY, dict, recipe_input.text, **QUICK_ACTIVITY
        )
        input_key = f"{workflow_id}/{run_id}/input"
        stored = await workflow.execute_activity(
            STORE_TRACE_ACTIVITY,
            dict,
            {"key": input_key, "params": self.params},
            **QUICK_ACTIVITY,
        )
        self.stored_path = stored["path"]
        await self.presentation_gate("input_stored")

        self.phase = "LOOKING UP GATEWAY LOGS AND DEPENDENCY GRAPH"
        gateway, graph = await asyncio.gather(
            self.lookup(
                "gateway logs",
                workflow.execute_activity(
                    GET_LOGS_ACTIVITY,
                    dict,
                    {
                        "service": self.params["service_name"],
                        "trace_id": self.params["trace_id"],
                        "scan_seconds": limits["scan_seconds"],
                        "rescan_seconds": limits["rescan_seconds"],
                    },
                    **SCAN_ACTIVITY,
                ),
            ),
            self.lookup(
                "dependency graph",
                workflow.execute_activity(
                    GRAPH_ACTIVITY,
                    dict,
                    {
                        "endpoint": self.params["endpoint_id"],
                        "service": self.params["service_name"],
                    },
                    **QUICK_ACTIVITY,
                ),
            ),
        )
        if gateway is None:
            return self.finish("gateway_logs_unavailable")
        upstream = next(
            (
                line["upstream"]
                for line in gateway["lines"]
                if line.get("upstream")
            ),
            None,
        )
        start = graph["depth1"][0] if graph else upstream

        await self.presentation_gate("lookups_complete")
        failure = await self.run_agent(
            start,
            self.params["trace_id"],
            limits["max_steps"],
            limits["repeat_limit"],
        )
        if failure:
            return self.finish(failure)

        self.phase = "AWAITING_GUIDANCE"
        while not self.guidance_notes and not self.decision:
            await workflow.wait_condition(
                lambda: bool(
                    self.guidance_notes
                    or self.decision
                    or self.pending_revisions
                )
            )
            if self.pending_revisions:
                self.phase = "REVISING FIRST DRAFT"
                self.conclusion = await workflow.execute_activity(
                    REVISE_ACTIVITY,
                    dict,
                    {
                        "conclusion": self.conclusion,
                        "request": self.pending_revisions.pop(0),
                        "hops": [gateway, *self.hops],
                    },
                    **MODEL_ACTIVITY,
                )
                self.revision += 1
                self.phase = "AWAITING_GUIDANCE"
        if self.decision:
            return self.finish("rejected" if self.decision != "approve" else "approved_wrong")

        self.phase = "REPLANNING WITH DURABLE GUIDANCE"
        self.calls = []
        self.hops = []
        self.guard = ""
        failure = await self.run_agent(
            start,
            self.params["trace_id"],
            limits["max_steps"],
            limits["repeat_limit"],
        )
        if failure:
            return self.finish(failure)

        for request in []:  # Past requests are not silently applied to the new draft.
            self.phase = "REVISING"
            self.conclusion = await workflow.execute_activity(
                REVISE_ACTIVITY,
                dict,
                {
                    "conclusion": self.conclusion,
                    "request": request,
                    "hops": [gateway, *self.hops],
                },
                **MODEL_ACTIVITY,
            )
            self.revision += 1

        expired: list[bool] = []

        async def approval_timer() -> None:
            try:
                await workflow.sleep(
                    timedelta(seconds=limits["approval_window_seconds"])
                )
            except asyncio.CancelledError:
                return
            expired.append(True)

        timer = asyncio.create_task(approval_timer())
        self.phase = "AWAITING_APPROVAL"
        while True:
            await workflow.wait_condition(
                lambda: bool(self.decision or self.pending_revisions or expired)
            )
            if self.decision or expired:
                break
            self.phase = "REVISING"
            self.conclusion = await workflow.execute_activity(
                REVISE_ACTIVITY,
                dict,
                {
                    "conclusion": self.conclusion,
                    "request": self.pending_revisions.pop(0),
                    "hops": [gateway, *self.hops],
                },
                **MODEL_ACTIVITY,
            )
            self.revision += 1
            self.phase = "AWAITING_APPROVAL"

        if expired:
            return self.finish("approval_expired")
        timer.cancel()
        if self.decision != "approve":
            return self.finish("rejected")
        self.phase = "UPLOADING"
        conclusion_key = f"{workflow_id}/{run_id}/conclusion"
        receipt = await workflow.execute_activity(
            UPLOAD_ACTIVITY,
            dict,
            {
                "key": conclusion_key,
                "conclusion": self.conclusion,
            },
            **QUICK_ACTIVITY,
        )
        return self.finish("conclusion_uploaded", receipt=receipt["receipt"])


def build_registry() -> Registry:
    registry = Registry()
    registry.workflow(IncidentTriageWorkflow)
    for activity_definition in ACTIVITIES:
        registry.register_activity(activity_definition)
    return registry
