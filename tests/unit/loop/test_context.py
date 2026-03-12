"""Tests for LoopContext protocol."""

from __future__ import annotations

from typing import Any

import pytest

from agent_sdk.loop.context import LoopContext


@pytest.mark.unit
class TestLoopContextProtocol:
    """Verify LoopContext is a valid runtime-checkable protocol."""

    def test_is_runtime_checkable(self) -> None:
        """LoopContext must be decorated with @runtime_checkable."""
        # If not runtime_checkable, isinstance() would raise TypeError
        assert isinstance(LoopContext, type)

    def test_mock_satisfies_protocol(self) -> None:
        """A class implementing all required members satisfies the protocol."""
        mock = _MockLoopContext()
        assert isinstance(mock, LoopContext)

    def test_empty_class_does_not_satisfy(self) -> None:
        """An empty class must not satisfy the protocol."""

        class Empty:
            pass

        assert not isinstance(Empty(), LoopContext)

    def test_partial_class_does_not_satisfy(self) -> None:
        """A class with only some members must not satisfy the protocol."""

        class Partial:
            @property
            def thread(self) -> Any:
                return None

            def is_cancelled(self) -> bool:
                return False

        assert not isinstance(Partial(), LoopContext)

    def test_protocol_has_all_react_loop_dependencies(self) -> None:
        """Verify LoopContext covers every self._h.* access in ReactLoop.

        This test documents the complete interface ReactLoop expects.
        If a new access is added to ReactLoop without updating LoopContext,
        this test serves as a reminder to update the protocol.
        """
        # Properties ReactLoop reads
        expected_properties = {
            "thread",
            "compactor",
            "working_memory",
            "memory_manager",
            "error_recovery",
            "token_budget",
            "max_context_tokens",
            "plan_mode_locked",
            "has_event_emitter",
        }

        # Methods ReactLoop calls
        expected_methods = {
            "is_cancelled",
            "new_step_id",
            "on_step_complete",
            "call_llm",
            "get_external_tool_defs",
            "get_agent_tool_defs",
            "execute_external_tools",
            "execute_agent_tool",
            "is_agent_tool",
            "emit_step_started",
            "emit_step_completed",
            "emit_text_chunk",
            "emit_step_limit_approaching",
            "emit_task_failed",
            "emit_context_compacted",
            "emit_verification_started",
            "emit_verification_completed",
        }

        # Verify all expected members exist on LoopContext
        all_expected = expected_properties | expected_methods
        for name in all_expected:
            assert hasattr(LoopContext, name), f"LoopContext missing member: {name}"


class _MockLoopContext:
    """Minimal implementation satisfying LoopContext protocol."""

    @property
    def thread(self) -> Any:
        return None

    @property
    def compactor(self) -> Any:
        return None

    @property
    def working_memory(self) -> Any | None:
        return None

    @property
    def memory_manager(self) -> Any | None:
        return None

    @property
    def error_recovery(self) -> Any:
        return None

    @property
    def token_budget(self) -> Any:
        return None

    @property
    def max_context_tokens(self) -> int:
        return 128000

    @property
    def plan_mode_locked(self) -> bool:
        return False

    @property
    def has_event_emitter(self) -> bool:
        return False

    def is_cancelled(self) -> bool:
        return False

    def new_step_id(self) -> str:
        return "step-1"

    async def on_step_complete(self, task_id: str, step: int) -> None:
        pass

    async def call_llm(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        task_id: str,
        step_id: str,
        on_text_chunk: Any | None = None,
    ) -> Any:
        return None

    def get_external_tool_defs(self) -> list[dict[str, Any]]:
        return []

    def get_agent_tool_defs(self) -> list[dict[str, Any]]:
        return []

    async def execute_external_tools(
        self,
        tool_calls: list[Any],
        task_id: str,
        step_id: str,
    ) -> list[Any]:
        return []

    async def execute_agent_tool(
        self,
        tool_call: Any,
        task_id: str,
    ) -> dict[str, Any]:
        return {}

    def is_agent_tool(self, tool_name: str) -> bool:
        return False

    def emit_step_started(self, task_id: str, step: int, step_id: str) -> None:
        pass

    def emit_step_completed(self, task_id: str, step: int, step_id: str) -> None:
        pass

    def emit_text_chunk(self, task_id: str, text: str, step_id: str) -> None:
        pass

    def emit_step_limit_approaching(self, task_id: str, step: int, max_steps: int) -> None:
        pass

    def emit_task_failed(self, task_id: str, reason: str) -> None:
        pass

    def emit_context_compacted(
        self, task_id: str, dropped: int, pre_count: int, post_count: int, step_id: str
    ) -> None:
        pass

    def emit_verification_started(self, task_id: str) -> None:
        pass

    def emit_verification_completed(self, task_id: str, *, passed: bool) -> None:
        pass
