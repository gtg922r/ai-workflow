"""Abstract base class for AI agent backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class AgentType(Enum):
    """Supported agent types."""

    CLAUDE = "claude"
    CURSOR = "cursor"


@dataclass
class AgentConfig:
    """Configuration for an agent backend."""

    working_dir: Path
    allow_network: bool = True
    allowed_tools: list[str] | None = None
    max_tokens: int | None = None
    timeout_seconds: int = 600  # 10 minutes default
    extra_args: list[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Result from an agent run."""

    success: bool
    output: str
    exit_code: int
    tokens_used: int | None = None
    cost: float | None = None
    error: str | None = None
    complete_signal: bool = False  # True if agent signaled <promise>COMPLETE</promise>
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def summary(self) -> str:
        """Generate a brief summary of the result."""
        if self.error:
            return f"Error: {self.error[:100]}"

        # Try to extract a meaningful summary from output
        lines = self.output.strip().split("\n")
        # Look for common summary patterns
        for line in reversed(lines[-20:]):
            line = line.strip()
            if line and len(line) < 200:
                # Skip common noise
                if not any(
                    skip in line.lower()
                    for skip in ["token", "cost", "duration", "---", "==="]
                ):
                    return line[:150]

        return "Run completed" if self.success else "Run failed"


class AgentBackend(ABC):
    """Abstract base class for agent backends."""

    agent_type: AgentType

    def __init__(self, config: AgentConfig):
        """Initialize the agent backend."""
        self.config = config

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this agent backend is available on the system."""
        ...

    @abstractmethod
    def get_version(self) -> str | None:
        """Get the version of the agent CLI, or None if unavailable."""
        ...

    @abstractmethod
    async def run(self, prompt: str) -> AgentResult:
        """Run the agent with the given prompt."""
        ...

    @abstractmethod
    def build_command(self, prompt: str) -> list[str]:
        """Build the command to execute for the agent."""
        ...

    def parse_output(self, output: str, exit_code: int) -> AgentResult:
        """Parse the output from the agent. Override for custom parsing."""
        success = exit_code == 0
        complete_signal = "<promise>COMPLETE</promise>" in output

        # Try to extract token/cost info from output
        tokens_used = self._extract_tokens(output)
        cost = self._extract_cost(output)

        return AgentResult(
            success=success,
            output=output,
            exit_code=exit_code,
            tokens_used=tokens_used,
            cost=cost,
            complete_signal=complete_signal,
        )

    def _extract_tokens(self, output: str) -> int | None:
        """Extract token count from output if present."""
        import re

        patterns = [
            r"tokens?[:\s]+(\d[\d,]+)",
            r"(\d[\d,]+)\s*tokens?",
        ]
        for pattern in patterns:
            match = re.search(pattern, output.lower())
            if match:
                return int(match.group(1).replace(",", ""))
        return None

    def _extract_cost(self, output: str) -> float | None:
        """Extract cost from output if present."""
        import re

        patterns = [
            r"\$(\d+\.?\d*)",
            r"cost[:\s]+\$?(\d+\.?\d*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, output.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        return None

