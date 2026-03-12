# cowork-agent-sdk

Reusable agent building blocks for the cowork project. Provides portable primitives for building agents: loop strategies, memory systems, policy enforcement, LLM client, token budget, context compaction, and more.

## Installation

```bash
# Development (local)
pip install -e "../cowork-platform[sdk]" -e ".[dev]"

# CI (from git)
pip install "cowork-platform[sdk] @ git+https://github.com/suman724/cowork-platform.git@main"
pip install "cowork-agent-sdk[dev] @ git+https://github.com/suman724/cowork-agent-sdk.git@main"
```

## Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
make install

# Run all checks
make check

# Run tests only
make test
```

## Package Structure

```
src/agent_sdk/
  loop/         — Loop strategies & protocols (LoopContext, ReactLoop)
  thread/       — Message thread, context compaction, token counting
  memory/       — Working memory, persistent memory, plan, task tracker
  policy/       — Policy enforcement (path/command/domain matchers)
  llm/          — LLM Gateway streaming client
  budget/       — Token budget tracking
  approval/     — Approval gate mechanism
  skills/       — Skill discovery & loading
  checkpoint/   — Crash recovery persistence
  tracking/     — File change tracking
```

## Usage

This package is used as a dependency by `cowork-agent-runtime`. The `LoopContext` protocol is the key interface — implement it in your runtime to use SDK loop strategies like `ReactLoop`.

## Design Doc

See `cowork-infra/docs/design/agent-sdk-extraction.md` for the full design and implementation plan.
