"""LoopContext — the interface a LoopStrategy needs from its runtime.

This is the central protocol for the agent SDK. Loop strategies like ReactLoop
depend on LoopContext (not a concrete LoopRuntime). Any runtime that satisfies
this protocol can drive a loop strategy.

Type annotations use Any for types that will be tightened as modules migrate
into agent_sdk (MessageThread, ContextCompactor, WorkingMemory, etc.).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LoopContext(Protocol):
    """Protocol that any loop strategy runtime must satisfy.

    Properties provide access to shared agent infrastructure.
    Methods provide actions the strategy can invoke.
    """

    # ── Properties ───────────────────────────────────────────

    @property
    def thread(self) -> Any:
        """Conversation thread (MessageThread)."""
        ...

    @property
    def compactor(self) -> Any:
        """Context compaction strategy (ContextCompactor)."""
        ...

    @property
    def working_memory(self) -> Any | None:
        """Working memory — task tracker, plan, notes (WorkingMemory)."""
        ...

    @property
    def memory_manager(self) -> Any | None:
        """Persistent memory manager (MemoryManager)."""
        ...

    @property
    def error_recovery(self) -> Any:
        """Error recovery tracker (ErrorRecovery)."""
        ...

    @property
    def token_budget(self) -> Any:
        """Token budget tracker (TokenBudget)."""
        ...

    @property
    def max_context_tokens(self) -> int:
        """Maximum context window size in tokens."""
        ...

    @property
    def plan_mode_locked(self) -> bool:
        """Whether plan mode is hard-locked (planOnly=true)."""
        ...

    @property
    def has_event_emitter(self) -> bool:
        """Whether an event emitter is configured (for streaming callbacks)."""
        ...

    # ── Lifecycle ────────────────────────────────────────────

    def is_cancelled(self) -> bool:
        """Check if the current task has been cancelled."""
        ...

    def new_step_id(self) -> str:
        """Generate a new unique step ID."""
        ...

    async def on_step_complete(self, task_id: str, step: int) -> None:
        """Invoke checkpoint callback after a step completes."""
        ...

    # ── LLM ──────────────────────────────────────────────────

    async def call_llm(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        task_id: str,
        step_id: str,
        on_text_chunk: Any | None = None,
    ) -> Any:
        """Call LLM with policy check + budget pre-check + streaming.

        Returns an LLMResponse.
        """
        ...

    # ── Tools ────────────────────────────────────────────────

    def get_external_tool_defs(self) -> list[dict[str, Any]]:
        """Tool definitions from ToolRouter (policy-filtered)."""
        ...

    def get_agent_tool_defs(self) -> list[dict[str, Any]]:
        """Agent-internal tool definitions (TaskTracker, memory, etc.)."""
        ...

    async def execute_external_tools(
        self,
        tool_calls: list[Any],
        task_id: str,
        step_id: str,
    ) -> list[Any]:
        """Execute tools through ToolExecutor (policy, approval, events).

        Returns list of ToolCallResult.
        """
        ...

    async def execute_agent_tool(
        self,
        tool_call: Any,
        task_id: str,
    ) -> dict[str, Any]:
        """Execute an agent-internal tool (no policy, no ToolRouter)."""
        ...

    def is_agent_tool(self, tool_name: str) -> bool:
        """Check if a tool name is agent-internal."""
        ...

    # ── Events ───────────────────────────────────────────────

    def emit_step_started(self, task_id: str, step: int, step_id: str) -> None:
        """Emit step_started event."""
        ...

    def emit_step_completed(self, task_id: str, step: int, step_id: str) -> None:
        """Emit step_completed event."""
        ...

    def emit_text_chunk(self, task_id: str, text: str, step_id: str) -> None:
        """Emit text_chunk event."""
        ...

    def emit_step_limit_approaching(self, task_id: str, step: int, max_steps: int) -> None:
        """Emit step_limit_approaching event."""
        ...

    def emit_task_failed(self, task_id: str, reason: str) -> None:
        """Emit task_failed event."""
        ...

    def emit_context_compacted(
        self, task_id: str, dropped: int, pre_count: int, post_count: int, step_id: str
    ) -> None:
        """Emit context_compacted event."""
        ...

    def emit_verification_started(self, task_id: str) -> None:
        """Emit verification_started event."""
        ...

    def emit_verification_completed(self, task_id: str, *, passed: bool) -> None:
        """Emit verification_completed event."""
        ...
