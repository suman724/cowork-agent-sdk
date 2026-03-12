# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

`cowork-agent-sdk` contains reusable agent building blocks extracted from `cowork-agent-runtime`. These are portable primitives that any agent built on the cowork platform can use — loop strategies, memory systems, policy enforcement, LLM client, token budget, context compaction, and more.

This package is a dependency of `cowork-agent-runtime`. It must never import from `agent_host` or `tool_runtime`.

## Architecture

```
agent_sdk/
  loop/           — Agent loop strategies & protocols (LoopContext, LoopStrategy, ReactLoop)
  thread/         — Conversation thread management, context compaction, token counting
  memory/         — Working memory, persistent memory, plan, task tracker, project instructions
  policy/         — Policy enforcement (pure, no I/O): capability validation, path/command/domain matchers
  llm/            — LLM Gateway streaming client (openai SDK), response models, error classifier
  budget/         — Token budget tracking (pre-check + record_usage)
  approval/       — Approval gate mechanism (asyncio Futures)
  skills/         — Skill discovery & loading (definitions, loader)
  checkpoint/     — Crash recovery persistence (checkpoint manager)
  tracking/       — File change tracking
```

## Key Concepts

- **LoopContext Protocol** (`loop/context.py`) — The central interface that any loop strategy needs from its runtime. Defines methods for LLM calls, tool execution, memory access, event emission. Implemented by `LoopRuntime` in `cowork-agent-runtime`.
- **LoopStrategy Protocol** (`loop/strategy.py`) — Single method `async def run(task_id) -> LoopResult`. Strategies compose LoopContext primitives.
- **ReactLoop** (`loop/react_loop.py`) — Default ReAct loop strategy. Depends on `LoopContext`, not concrete `LoopRuntime`.

## Dependency Rules

- **Allowed**: `cowork-platform[sdk]`, stdlib, and declared third-party dependencies
- **Prohibited**: `agent_host`, `tool_runtime`, or any cowork service repo

## Engineering Standards

### Python Tooling

- **Python**: 3.12+
- **Linting/formatting**: `ruff` (line length 100)
- **Type checking**: `mypy --strict`
- **Testing**: `pytest` with `pytest-asyncio`
- **Coverage**: 90% minimum

### Makefile Targets

```
make help          # Show all targets
make install       # Install dependencies
make lint          # Run ruff check
make format        # Run ruff format
make format-check  # Check formatting
make typecheck     # Run mypy --strict
make test          # Run unit tests
make build         # Build wheel
make check         # CI gate: lint + format-check + typecheck + test
make clean         # Remove build artifacts
```

## Design Doc

Full specification: `cowork-infra/docs/design/agent-sdk-extraction.md`
