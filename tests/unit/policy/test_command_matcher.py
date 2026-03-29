"""Tests for shell command matching."""

from __future__ import annotations

from agent_sdk.policy.command_matcher import (
    check_command,
    extract_base_command,
    matches_command_pattern,
)


class TestExtractBaseCommand:
    def test_simple_command(self) -> None:
        assert extract_base_command("ls -la") == "ls"

    def test_with_path_prefix(self) -> None:
        assert extract_base_command("/usr/bin/git status") == "git"

    def test_with_backslash_in_token(self) -> None:
        """Backslash path stripping works when token contains literal backslash."""
        # Use a raw string to avoid shlex consuming the backslashes
        assert extract_base_command(r'"C:\Python39\python.exe" script.py') == "python.exe"

    def test_malformed_quoting(self) -> None:
        """Malformed quoting falls back to whitespace split."""
        assert extract_base_command("echo 'unterminated") == "echo"

    def test_empty_command(self) -> None:
        assert extract_base_command("") == ""

    def test_command_with_args(self) -> None:
        assert extract_base_command("python -m pytest tests/") == "python"

    def test_command_with_chaining(self) -> None:
        """Extracts only the first command from chained commands."""
        assert extract_base_command("cd /tmp && ls") == "cd"


class TestCheckCommand:
    def test_allowed_command(self) -> None:
        allowed, reason = check_command("git status", ["git", "npm"], None)
        assert allowed
        assert reason == ""

    def test_blocked_command(self) -> None:
        allowed, reason = check_command("rm -rf /", None, ["rm", "dd"])
        assert not allowed
        assert "blocked" in reason

    def test_blocklist_precedence(self) -> None:
        """Blocklist takes precedence over allowlist."""
        allowed, _reason = check_command("rm file.txt", ["rm"], ["rm"])
        assert not allowed

    def test_no_lists_allows_all(self) -> None:
        allowed, _reason = check_command("anything", None, None)
        assert allowed

    def test_not_in_allowlist(self) -> None:
        allowed, reason = check_command("curl http://x", ["git", "npm"], None)
        assert not allowed
        assert "not in allowed list" in reason

    def test_empty_command(self) -> None:
        allowed, reason = check_command("", None, None)
        assert not allowed
        assert "Empty command" in reason

    def test_empty_allowlist(self) -> None:
        """Empty allowlist [] is falsy, so treated as 'no restriction'."""
        allowed, _ = check_command("git status", [], None)
        assert allowed

    # --- Pattern-based matching (A8) ---

    def test_blocked_pattern_git_force_push(self) -> None:
        allowed, reason = check_command(
            "git push --force origin main",
            ["git *"],
            ["git push --force *"],
        )
        assert not allowed
        assert "blocked by pattern" in reason

    def test_allowed_pattern_git_wildcard(self) -> None:
        allowed, _ = check_command("git status", ["git *"], None)
        assert allowed

    def test_allowed_pattern_subcommand(self) -> None:
        allowed, _ = check_command("git push origin main", ["git push *"], None)
        assert allowed

    def test_not_allowed_pattern_mismatch(self) -> None:
        allowed, _ = check_command("npm install", ["git *"], None)
        assert not allowed

    def test_base_only_backward_compat_with_patterns(self) -> None:
        """Simple base-only entries still work alongside patterns."""
        allowed, _ = check_command("npm install express", ["git *", "npm"], None)
        assert allowed

    def test_blocked_pattern_rm_rf_root(self) -> None:
        allowed, reason = check_command("rm -rf /", None, ["rm -rf /"])
        assert not allowed
        assert "blocked by pattern" in reason

    def test_allowed_rm_specific_file_not_blocked(self) -> None:
        """rm of a specific file should not be blocked by 'rm -rf /' pattern."""
        allowed, _ = check_command("rm temp.txt", None, ["rm -rf /", "rm -rf ~"])
        assert allowed


class TestMatchesCommandPattern:
    def test_exact_subcommand(self) -> None:
        assert matches_command_pattern("git push", "git push")

    def test_wildcard_matches_remaining(self) -> None:
        assert matches_command_pattern("git push origin main", "git push *")

    def test_wildcard_matches_zero_remaining(self) -> None:
        assert matches_command_pattern("git push", "git push *")

    def test_no_match_different_base(self) -> None:
        assert not matches_command_pattern("npm install", "git *")

    def test_no_match_different_subcommand(self) -> None:
        assert not matches_command_pattern("git status", "git push")

    def test_base_only_matches(self) -> None:
        assert matches_command_pattern("git status", "git")

    def test_flags_match(self) -> None:
        assert matches_command_pattern("git push --force origin", "git push --force *")

    def test_flags_no_match(self) -> None:
        assert not matches_command_pattern("git push origin", "git push --force *")

    def test_path_prefix_stripped(self) -> None:
        assert matches_command_pattern("/usr/bin/git push", "git push")

    def test_empty_command(self) -> None:
        assert not matches_command_pattern("", "git")

    def test_empty_pattern(self) -> None:
        assert not matches_command_pattern("git status", "")
