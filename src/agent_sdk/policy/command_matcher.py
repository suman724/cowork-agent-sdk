"""Shell command matching — extracts base command and checks allow/block lists.

Supports two matching modes:
- Base command matching (backward compat): "git" matches any command starting with git
- Pattern matching: "git push --force *" matches commands with those specific tokens
"""

from __future__ import annotations

import shlex


def extract_base_command(command: str) -> str:
    """Extract the base command name from a shell command string.

    Examples:
        "pytest tests/ --verbose" -> "pytest"
        "python -m build" -> "python"
        "/usr/bin/git status" -> "git"
        "cd /tmp && ls -la" -> "cd"
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        # Malformed quoting — fall back to whitespace split
        tokens = command.split()

    if not tokens:
        return ""

    first = tokens[0]
    # Strip path prefix: /usr/bin/git -> git
    if "/" in first:
        first = first.rsplit("/", maxsplit=1)[-1]
    if "\\" in first:
        first = first.rsplit("\\", maxsplit=1)[-1]

    return first


def _is_pattern(entry: str) -> bool:
    """Check if a policy entry is a pattern (has spaces or wildcards) vs base-only."""
    return " " in entry or "*" in entry


def matches_command_pattern(command: str, pattern: str) -> bool:
    """Match a full command string against a pattern.

    Patterns:
    - "git" → matches base command only (backward compatible)
    - "git push" → matches command + subcommand
    - "git push --force *" → matches with specific flags, * matches rest
    - "rm -rf *" → matches rm with -rf flag and any arguments

    The wildcard * matches zero or more remaining tokens.
    """
    try:
        cmd_parts = shlex.split(command)
    except ValueError:
        cmd_parts = command.split()

    try:
        pattern_parts = shlex.split(pattern)
    except ValueError:
        pattern_parts = pattern.split()

    if not cmd_parts or not pattern_parts:
        return False

    # Strip path prefix from command's first token for comparison
    cmd_first = cmd_parts[0]
    if "/" in cmd_first:
        cmd_first = cmd_first.rsplit("/", maxsplit=1)[-1]
    if "\\" in cmd_first:
        cmd_first = cmd_first.rsplit("\\", maxsplit=1)[-1]

    for i, pat in enumerate(pattern_parts):
        if pat == "*":
            return True  # Wildcard matches zero or more remaining tokens
        cmd_token = cmd_first if i == 0 else (cmd_parts[i] if i < len(cmd_parts) else None)
        if cmd_token is None:
            return False  # Pattern longer than command
        if pat != cmd_token:
            return False  # Mismatch

    # Pattern exhausted — matches (command may have more tokens)
    return True


def check_command(
    command: str,
    allowed_commands: list[str] | None,
    blocked_commands: list[str] | None,
) -> tuple[bool, str]:
    """Check whether a shell command is permitted by the policy.

    Args:
        command: The full command string.
        allowed_commands: Command allowlist (base names or patterns). If None, all allowed.
        blocked_commands: Command blocklist (base names or patterns). Takes precedence.

    Returns:
        (allowed, reason) tuple.
    """
    base = extract_base_command(command)

    if not base:
        return False, "Empty command"

    # Blocklist takes precedence
    if blocked_commands:
        for entry in blocked_commands:
            if _is_pattern(entry):
                if matches_command_pattern(command, entry):
                    return False, f"Command blocked by pattern: {entry}"
            elif base == entry:
                return False, f"Command blocked: {base}"

    # If no allowlist, everything not blocked is allowed
    if not allowed_commands:
        return True, ""

    for entry in allowed_commands:
        if _is_pattern(entry):
            if matches_command_pattern(command, entry):
                return True, ""
        elif base == entry:
            return True, ""

    return False, f"Command not in allowed list: {base}"
