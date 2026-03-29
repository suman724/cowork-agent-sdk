"""Tests for risk level assessment."""

from __future__ import annotations

from cowork_platform_sdk import CapabilityName, RiskLevel

from agent_sdk.policy.risk_assessor import assess_command_risk, assess_risk


class TestAssessRisk:
    def test_file_read_is_low(self) -> None:
        assert assess_risk("ReadFile", CapabilityName.FILE_READ, {}) == RiskLevel.LOW

    def test_file_write_is_medium(self) -> None:
        assert assess_risk("WriteFile", CapabilityName.FILE_WRITE, {}) == RiskLevel.MEDIUM

    def test_file_delete_is_high(self) -> None:
        assert assess_risk("DeleteFile", CapabilityName.FILE_DELETE, {}) == RiskLevel.HIGH

    def test_shell_exec_is_medium(self) -> None:
        assert assess_risk("RunCommand", CapabilityName.SHELL_EXEC, {}) == RiskLevel.MEDIUM

    def test_network_http_is_medium(self) -> None:
        assert assess_risk("HttpRequest", CapabilityName.NETWORK_HTTP, {}) == RiskLevel.MEDIUM

    def test_workspace_upload_is_low(self) -> None:
        assert assess_risk("Upload", CapabilityName.WORKSPACE_UPLOAD, {}) == RiskLevel.LOW

    def test_backend_tool_invoke_is_medium(self) -> None:
        assert (
            assess_risk("BackendTool", CapabilityName.BACKEND_TOOL_INVOKE, {}) == RiskLevel.MEDIUM
        )

    def test_unknown_capability_is_high(self) -> None:
        assert assess_risk("Unknown", "SomeUnknown.Capability", {}) == RiskLevel.HIGH

    # --- Shell argument inspection (A8) ---

    def test_shell_exec_dangerous_command_elevated_to_high(self) -> None:
        risk = assess_risk("RunCommand", CapabilityName.SHELL_EXEC, {"command": "rm -rf /"})
        assert risk == RiskLevel.HIGH

    def test_shell_exec_force_push_elevated_to_high(self) -> None:
        risk = assess_risk(
            "RunCommand", CapabilityName.SHELL_EXEC, {"command": "git push --force origin"}
        )
        assert risk == RiskLevel.HIGH

    def test_shell_exec_normal_command_stays_medium(self) -> None:
        risk = assess_risk("RunCommand", CapabilityName.SHELL_EXEC, {"command": "git status"})
        assert risk == RiskLevel.MEDIUM

    def test_shell_exec_no_command_arg_stays_medium(self) -> None:
        """Missing command argument should not crash — defaults to medium."""
        risk = assess_risk("RunCommand", CapabilityName.SHELL_EXEC, {})
        assert risk == RiskLevel.MEDIUM


class TestAssessCommandRisk:
    def test_rm_rf_root(self) -> None:
        assert assess_command_risk("rm -rf /") == "high"

    def test_rm_rf_home(self) -> None:
        assert assess_command_risk("rm -rf ~") == "high"

    def test_rm_rf_dot(self) -> None:
        assert assess_command_risk("rm -rf .") == "high"

    def test_git_force_push(self) -> None:
        assert assess_command_risk("git push --force origin main") == "high"

    def test_git_force_push_short_flag(self) -> None:
        assert assess_command_risk("git push -f origin main") == "high"

    def test_git_reset_hard(self) -> None:
        assert assess_command_risk("git reset --hard HEAD~3") == "high"

    def test_chmod_777(self) -> None:
        assert assess_command_risk("chmod 777 /etc/passwd") == "high"

    def test_dd(self) -> None:
        assert assess_command_risk("dd if=/dev/zero of=/dev/sda") == "high"

    def test_mkfs(self) -> None:
        assert assess_command_risk("mkfs.ext4 /dev/sda1") == "high"

    def test_normal_git(self) -> None:
        assert assess_command_risk("git status") == "low"

    def test_normal_rm(self) -> None:
        assert assess_command_risk("rm temp.txt") == "low"

    def test_npm_install(self) -> None:
        assert assess_command_risk("npm install express") == "low"

    def test_empty_command(self) -> None:
        assert assess_command_risk("") == "low"
