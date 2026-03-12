"""cowork-agent-sdk: Reusable agent building blocks for the cowork platform.

Public API — key types re-exported for convenience:

    LoopContext: Protocol that loop strategies require from their runtime.
    LoopStrategy: Protocol for agent loop implementations.
    ReactLoop: Default linear ReAct loop strategy.
    LoopResult: Return type from loop strategies.
    PolicyEnforcer: Pure capability validation (no I/O).
    TokenBudget: Token usage tracking with pre-check.
    MessageThread: Conversation history management.
    MemoryManager: Persistent memory orchestrator.
    WorkingMemory: Structured per-task agent state.
    LLMClient: LLM Gateway streaming client.
    SkillLoader: Skill discovery and loading.
    CheckpointManager: Crash recovery persistence.
    FileChangeTracker: File mutation tracking for patch preview.
"""

from agent_sdk.checkpoint.checkpoint_manager import CheckpointManager
from agent_sdk.llm.client import LLMClient
from agent_sdk.loop.context import LoopContext
from agent_sdk.loop.models import LoopResult
from agent_sdk.loop.react_loop import ReactLoop
from agent_sdk.loop.strategy import LoopStrategy
from agent_sdk.memory.memory_manager import MemoryManager
from agent_sdk.memory.working_memory import WorkingMemory
from agent_sdk.policy.policy_enforcer import PolicyEnforcer
from agent_sdk.skills.skill_loader import SkillLoader
from agent_sdk.thread.message_thread import MessageThread
from agent_sdk.tracking.file_change_tracker import FileChangeTracker

__all__ = [
    "CheckpointManager",
    "FileChangeTracker",
    "LLMClient",
    "LoopContext",
    "LoopResult",
    "LoopStrategy",
    "MemoryManager",
    "MessageThread",
    "PolicyEnforcer",
    "ReactLoop",
    "SkillLoader",
    "WorkingMemory",
]
