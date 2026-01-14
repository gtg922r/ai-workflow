"""Abstract base class for AI agent backends."""

from __future__ import annotations

import asyncio
import os
import re
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
    def build_command(self, prompt: str) -> list[str]:
        """Build the command to execute for the agent."""
        ...

    def get_environment(self) -> dict[str, str] | None:
        """Get custom environment variables for the subprocess.

        Override in subclasses to provide agent-specific env vars.
        Returns None to use the default environment.
        """
        return None

    async def run(self, prompt: str) -> AgentResult:
        """Run the agent with the given prompt.

        This method handles subprocess execution, timeout, and error handling.
        Subclasses should override build_command() and optionally get_environment().
        """
        try:
            cmd = self.build_command(prompt)
        except RuntimeError as e:
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=str(e),
            )

        return await self._execute_subprocess(cmd)

    async def _execute_subprocess(self, cmd: list[str]) -> AgentResult:
        """Execute a subprocess command and return the result.

        Handles timeout, errors, and output capture consistently.
        """
        env = self.get_environment()
        if env is None:
            env = os.environ.copy()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.config.working_dir,
                env=env,
            )

            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds,
                )
                output = stdout.decode("utf-8", errors="replace")
                exit_code = process.returncode or 0
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return AgentResult(
                    success=False,
                    output="",
                    exit_code=-1,
                    error=f"Timeout after {self.config.timeout_seconds}s",
                )

        except FileNotFoundError:
            cli_name = cmd[0] if cmd else "CLI"
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=f"{cli_name} executable not found",
            )
        except Exception as e:
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=str(e),
            )

        return self.parse_output(output, exit_code)

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

    async def _run_subprocess(
        self,
        cmd: list[str],
        *,
        cli_label: str,
        env: dict[str, str] | None = None,
    ) -> tuple[str, int, str | None]:
        """Run the agent CLI subprocess and return output, exit code, and error."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.config.working_dir,
                env=env,
            )

            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds,
                )
                output = stdout.decode("utf-8", errors="replace")
                exit_code = process.returncode or 0
                return output, exit_code, None
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return "", -1, f"Timeout after {self.config.timeout_seconds}s"

        except FileNotFoundError:
            return "", -1, f"{cli_label} executable not found"
        except Exception as e:
            return "", -1, str(e)

    def _extract_tokens(self, output: str) -> int | None:
        """Extract token count from output if present."""
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
