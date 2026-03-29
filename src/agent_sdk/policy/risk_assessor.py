"""Risk level assessment for tool calls requiring approval."""

from __future__ import annotations

from typing import Literal

from cowork_platform_sdk import CapabilityName, RiskLevel

# Shell argument patterns that indicate destructive or dangerous operations.
# Checked via substring match against the full command string.
_HIGH_RISK_COMMAND_PATTERNS: list[str] = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf .",
    "git push --force",
    "git push -f",
    "git reset --hard",
    "chmod 777",
    "dd if=",
    "mkfs",
    "> /dev/",
]


def assess_command_risk(command: str) -> Literal["high", "low"]:
    """Assess risk of a shell command based on argument patterns.

    Uses substring matching against known destructive patterns.
    Returns "high" if any dangerous pattern is found, "low" otherwise.
    """
    for pattern in _HIGH_RISK_COMMAND_PATTERNS:
        if pattern in command:
            return "high"
    return "low"


def assess_risk(
    tool_name: str,  # noqa: ARG001
    capability_name: str,
    arguments: dict[str, object],
) -> Literal["low", "medium", "high"]:
    """Assess the risk level of a tool call.

    Args:
        tool_name: The tool name (reserved for future per-tool risk rules).
        capability_name: The capability being invoked.
        arguments: Tool call arguments (used for shell command argument inspection).

    Returns:
        Risk level: "low", "medium", or "high".
    """
    if capability_name == CapabilityName.FILE_READ:
        return RiskLevel.LOW

    if capability_name == CapabilityName.FILE_WRITE:
        return RiskLevel.MEDIUM

    if capability_name == CapabilityName.FILE_DELETE:
        return RiskLevel.HIGH

    if capability_name == CapabilityName.SHELL_EXEC:
        # Elevate risk based on command arguments
        command = str(arguments.get("command", ""))
        if command and assess_command_risk(command) == "high":
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM

    if capability_name == CapabilityName.NETWORK_HTTP:
        return RiskLevel.MEDIUM

    if capability_name == CapabilityName.WORKSPACE_UPLOAD:
        return RiskLevel.LOW

    if capability_name == CapabilityName.BACKEND_TOOL_INVOKE:
        return RiskLevel.MEDIUM

    # Unknown capability — default to high
    return RiskLevel.HIGH
