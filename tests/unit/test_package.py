"""Verify the agent_sdk package is importable."""

import pytest


@pytest.mark.unit
def test_import_agent_sdk() -> None:
    import agent_sdk

    assert agent_sdk is not None
