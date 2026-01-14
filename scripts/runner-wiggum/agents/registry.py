"""Agent backend registry and factory helpers."""

from __future__ import annotations

from pathlib import Path

from .base import AgentConfig, AgentType
from .claude import ClaudeAgent
from .cursor import CursorAgent


def create_agent(agent_type: AgentType, config: AgentConfig):
    """Create an agent backend for the given type."""
    if agent_type == AgentType.CLAUDE:
        return ClaudeAgent(config)
    if agent_type == AgentType.CURSOR:
        return CursorAgent(config)
    raise ValueError(f"Unsupported agent type: {agent_type}")


def list_available_agents(
    working_dir: Path,
) -> list[tuple[AgentType, bool, str | None]]:
    """List available agents and their versions."""
    results = []
    for agent_type in AgentType:
        config = AgentConfig(working_dir=working_dir)
        agent = create_agent(agent_type, config)
        available = agent.is_available()
        version = agent.get_version() if available else None
        results.append((agent_type, available, version))
    return results
