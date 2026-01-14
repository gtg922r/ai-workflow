"""Agent backend adapters for different AI CLI tools."""

from .base import AgentBackend, AgentResult
from .claude import ClaudeAgent
from .cursor import CursorAgent

__all__ = ["AgentBackend", "AgentResult", "ClaudeAgent", "CursorAgent"]

