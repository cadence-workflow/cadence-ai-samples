import io
import json
import os
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cadence.api.v1 import workflow_pb2
from cadence.contrib.pydantic import PydanticDataConverter
from cadence.error import WorkflowExecutionAlreadyStartedError
from cadence.testing import TestWorkflowEnvironment
from grpc import StatusCode

import activities
import main
import story
from durability_manifest import validate_manifest
from raw_agent import RawAgent
from run_compare import cadence_metrics, raw_metrics
from workflow import (
    GUIDANCE_SIGNAL,
    QUICK_ACTIVITY,
    REVISE_SIGNAL,
    STATUS_QUERY,
    WORKFLOW,
    RecipeInput,
    build_registry,
)


def environment() -> TestWorkflowEnvironment:
    return TestWorkflowEnvironment(
        build_registry(), data_converter=PydanticDataConverter()
    )


def fake_client(**start_workflow: object) -> SimpleNamespace:
    return SimpleNamespace(
        start_workflow=AsyncMock(**start_workflow), close=AsyncMock()
    )


class StoryTests(unittest.TestCase):
    def test_scripted_planner_takes_wrong_then_correct_paths(self) -> None:
        checkout = story.logs_for("checkout", "4bf92f3577b34da6")
        wrong = story.next_hop(checkout, [])
        right = story.next_hop(checkout, [story.GUIDANCE])
        self.assertEqual((wrong, right), ("inventory", "payments"))

        hops = [
            story.logs_for(service, "4bf92f3577b34da6")
            for service in ("checkout", "payments", "ledger")
        ]
        conclusion = story.conclusion(hops, True)
        self.assertEqual(conclusion["root_cause"], story.RIGHT_ROOT_CAUSE)
        self.assertEqual(conclusion["call_path"], story.CORRECT_PATH)

    def test_fixtures_are_synthetic_and_complete(self) -> None:
        trace = json.loads(story.trace_text())
        self.assertTrue(trace["synthetic"])
        self.assertEqual(story.dependency_graph()["depth1"], ["checkout"])
        for service in ("api-gateway", "checkout", "inventory", "payments", "ledger"):
            self.assertTrue(story.logs_for(service, trace["trace_id"])["lines"])


class RawAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_capable_raw_baseline_handles_retry_and_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            agent = RawAgent("raw-test", "first", Path(directory))
            wrong = await agent.run_pass("initial", [], inject_429=True)
            self.assertEqual(wrong.conclusion["root_cause"], story.WRONG_ROOT_CAUSE)
            right = await agent.run_pass(
                "manual-rerun", [story.GUIDANCE], inject_429=False
            )
            self.assertEqual(right.conclusion["root_cause"], story.RIGHT_ROOT_CAUSE)
            entries = [
                json.loads(line)
                for line in agent.ledger.read_text().splitlines()
            ]
            gateway = [
                (entry["attempt"], entry["status"])
                for entry in entries
                if entry["tool"] == "get_logs_by_trace_id"
                and entry["service"] == "api-gateway"
            ]
            self.assertEqual(gateway[:2], [(0, 429), (1, 200)])


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_guidance_reuses_setup_before_durable_timer_expires(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"INCIDENT_TRIAGE_STATE": directory}
        ):
            workflow_id = "offline-guided"
            with environment() as env:
                execution = await env.client.start_workflow(
                    WORKFLOW,
                    RecipeInput(
                        story.trace_text(),
                        {
                            "approval_window_seconds": 1000,
                            "scan_seconds": 0,
                            "rescan_seconds": 0,
                        },
                    ),
                    workflow_id=workflow_id,
                    task_list="test-task-list",
                )
                status = await env.client.query_workflow(
                    workflow_id,
                    execution.run_id,
                    STATUS_QUERY,
                    result_type=dict,
                )
                self.assertEqual(
                    status["phase"], "AWAITING_GUIDANCE", status
                )
                self.assertEqual(
                    status["conclusion"]["root_cause"], story.WRONG_ROOT_CAUSE
                )
                await env.client.signal_workflow(
                    workflow_id, execution.run_id, REVISE_SIGNAL, story.REVISION
                )
                revised = await env.client.query_workflow(
                    workflow_id,
                    execution.run_id,
                    STATUS_QUERY,
                    result_type=dict,
                )
                self.assertEqual(revised["revision"], 1)
                await env.client.signal_workflow(
                    workflow_id, execution.run_id, GUIDANCE_SIGNAL, story.GUIDANCE
                )
                result = env.get_workflow_result(
                    dict, workflow_id, execution.run_id
                )
            self.assertEqual(result["outcome"], "approval_expired")
            self.assertEqual(
                result["conclusion"]["root_cause"], story.RIGHT_ROOT_CAUSE
            )
            entries = [
                json.loads(line)
                for line in (Path(directory) / "ledger.jsonl").read_text().splitlines()
            ]
            names = [entry["tool"] for entry in entries]
            self.assertEqual(names.count("identify_input_params"), 1)
            self.assertEqual(names.count("store_trace"), 1)
            self.assertEqual(names.count("fetch_dependency_graph"), 1)
            self.assertEqual(names.count("upload_conclusion"), 0)

    def test_retry_policy_is_bounded_and_strict(self) -> None:
        retry = QUICK_ACTIVITY["retry_policy"]
        self.assertEqual(retry["maximum_attempts"], 3)
        self.assertIn(
            activities.NonRetryableHttpError.__name__,
            retry["non_retryable_error_reasons"],
        )


class ActivityTests(unittest.TestCase):
    def test_upload_is_idempotent_after_a_lost_reply(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"INCIDENT_TRIAGE_STATE": directory}
        ), patch(
            "activities.activity.info",
            return_value=SimpleNamespace(
                attempt=0, workflow_id="activity-test"
            ),
        ):
            request = {"key": "activity-test/conclusion", "conclusion": {"ok": True}}
            first = activities.upload_conclusion(request)
            second = activities.upload_conclusion(request)
        self.assertTrue(first["committed"])
        self.assertFalse(second["committed"])
        self.assertEqual(first["receipt"], second["receipt"])


class EvidenceTests(unittest.TestCase):
    def test_manifest_is_symmetric_and_has_no_overlaps(self) -> None:
        counts = validate_manifest()
        self.assertEqual(set(counts), {"raw", "cadence"})
        for side in counts.values():
            self.assertGreater(side["retry"], 0)
            self.assertGreater(side["state"], 0)
            self.assertGreater(side["deduplication"], 0)

    def test_comparison_reports_observed_calls_not_tokens(self) -> None:
        raw = raw_metrics(
            {
                "wall_seconds": 1.0,
                "process_seconds_waiting_for_human": 0.5,
                "root_cause": story.RIGHT_ROOT_CAUSE,
                "call_path": story.CORRECT_PATH,
                "outcome": "conclusion_uploaded",
            },
            [
                {"tool": "plan_next", "pass_id": "initial"},
                {"tool": "upload_conclusion", "pass_id": "restart"},
            ],
        )
        cadence = cadence_metrics(
            {
                "ledger": {"plan_next": 1, "upload_conclusion": 1},
                "final": {
                    "outcome": "conclusion_uploaded",
                    "conclusion": {
                        "root_cause": story.RIGHT_ROOT_CAUSE,
                        "call_path": story.CORRECT_PATH,
                    },
                },
                "zero_worker_seconds": 0.5,
                "history_events_at_zero_workers": 10,
            },
            1.2,
        )
        for metrics in (raw, cadence):
            self.assertIn("observed_model_calls", metrics)
            self.assertNotIn("tokens", metrics)
            self.assertFalse(metrics["provider_called"])
            self.assertFalse(metrics["tokenizer_run"])


class CommandTests(unittest.IsolatedAsyncioTestCase):
    def test_worker_and_start_share_defaults(self) -> None:
        worker = main.parser().parse_args(["worker", "--mode", "mock"])
        start = main.parser().parse_args(["start", "--mode", "live"])
        for args in (worker, start):
            self.assertEqual(args.domain, "cadence-ai-samples")
            self.assertEqual(args.task_list, "incident-triage")
            self.assertEqual(args.workflow_id, "incident-triage-demo")
        self.assertEqual(worker.mode, "mock")
        self.assertEqual(start.mode, "live")
        self.assertTrue(json.loads(start.text)["synthetic"])

    def test_overrides_and_invalid_commands(self) -> None:
        args = main.parser().parse_args(
            [
                "--task-list",
                "tl",
                "--workflow-id",
                "wf",
                "start",
                "--mode",
                "mock",
                "--text",
                story.trace_text(),
            ]
        )
        self.assertEqual((args.task_list, args.workflow_id), ("tl", "wf"))
        for argv in (
            [],
            ["stop"],
            ["worker"],
            ["start"],
            ["worker", "--mode", "other"],
            ["worker", "--mode", "mock", "--text", "hi"],
        ):
            with self.subTest(argv=argv), self.assertRaises(SystemExit), patch(
                "sys.stderr"
            ):
                main.parser().parse_args(argv)

    async def test_start_uses_allow_duplicate_after_closed_runs(self) -> None:
        cadence_client = fake_client(
            return_value=SimpleNamespace(
                workflow_id="incident-triage-demo", run_id="r1"
            )
        )
        with patch("main.client", return_value=cadence_client), patch(
            "builtins.print"
        ):
            await main.start(
                main.parser().parse_args(["start", "--mode", "mock"])
            )
        options = cadence_client.start_workflow.call_args.kwargs
        self.assertEqual(options["workflow_id"], "incident-triage-demo")
        self.assertEqual(
            options["workflow_id_reuse_policy"],
            workflow_pb2.WORKFLOW_ID_REUSE_POLICY_ALLOW_DUPLICATE,
        )
        self.assertEqual(
            options["execution_start_to_close_timeout"],
            main.WORKFLOW_EXECUTION_TIMEOUT,
        )
        self.assertGreater(
            options["execution_start_to_close_timeout"], timedelta(days=3)
        )
        cadence_client.close.assert_awaited_once()

    async def test_start_reports_an_open_duplicate(self) -> None:
        duplicate = WorkflowExecutionAlreadyStartedError(
            "already started", StatusCode.ALREADY_EXISTS, "request", "open-run"
        )
        cadence_client = fake_client(side_effect=duplicate)
        with patch("main.client", return_value=cadence_client), patch(
            "sys.stderr", new_callable=io.StringIO
        ) as stderr, self.assertRaises(SystemExit) as exit_info:
            await main.main(["start", "--mode", "mock"])
        self.assertEqual(exit_info.exception.code, 2)
        self.assertIn(
            "workflow-id=incident-triage-demo already has an open Run",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
