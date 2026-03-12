"""Tests for ReactLoop — construction with mock LoopContext."""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock

from agent_sdk.loop.context import LoopContext
from agent_sdk.loop.models import LoopResult
from agent_sdk.loop.react_loop import ReactLoop
from agent_sdk.loop.verification import VerificationConfig


def _make_mock_context() -> MagicMock:
    """Build a MagicMock satisfying LoopContext property signatures."""
    ctx = MagicMock(spec=LoopContext)
    type(ctx).plan_mode_locked = PropertyMock(return_value=False)
    type(ctx).has_event_emitter = PropertyMock(return_value=False)
    type(ctx).max_context_tokens = PropertyMock(return_value=128_000)
    type(ctx).working_memory = PropertyMock(return_value=None)
    type(ctx).memory_manager = PropertyMock(return_value=None)
    return ctx


class TestReactLoopConstruction:
    def test_constructs_with_mock_context(self) -> None:
        """ReactLoop should accept any LoopContext, not just LoopRuntime."""
        ctx = _make_mock_context()
        loop = ReactLoop(harness=ctx, max_steps=10)
        assert loop._max_steps == 10

    def test_constructs_with_verification(self) -> None:
        ctx = _make_mock_context()
        vc = VerificationConfig(enabled=True, max_verify_steps=5)
        loop = ReactLoop(harness=ctx, max_steps=10, verification=vc)
        assert loop._verification is vc


class TestReactLoopCancellation:
    async def test_returns_cancelled_immediately(self) -> None:
        """If context reports cancelled, loop should exit immediately."""
        ctx = _make_mock_context()
        ctx.is_cancelled.return_value = True
        ctx.new_step_id.return_value = "s-1"

        loop = ReactLoop(harness=ctx, max_steps=10)
        result = await loop.run("task-1")

        assert result.reason == "cancelled"
        assert result.step_count == 0


class TestReactLoopCompletion:
    async def test_completes_on_stop_without_tool_calls(self) -> None:
        """Loop should complete when LLM returns stop with no tool calls."""
        ctx = _make_mock_context()
        ctx.is_cancelled.return_value = False
        ctx.new_step_id.return_value = "s-1"
        ctx.get_external_tool_defs.return_value = []
        ctx.get_agent_tool_defs.return_value = []

        # Mock LLM response: text only, no tool calls, stop
        llm_response = MagicMock()
        llm_response.text = "Done!"
        llm_response.tool_calls = []
        llm_response.stop_reason = "stop"
        ctx.call_llm.return_value = llm_response

        # Mock thread
        ctx.thread.build_llm_payload.return_value = [{"role": "system", "content": "sys"}]
        ctx.thread.message_count = 1

        # Mock error recovery
        ctx.error_recovery.detect_loop.return_value = False
        ctx.error_recovery.should_inject_reflection.return_value = False

        loop = ReactLoop(harness=ctx, max_steps=10)
        result = await loop.run("task-1")

        assert result == LoopResult(reason="completed", text="Done!", step_count=1)
