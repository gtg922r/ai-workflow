"""Claude Code CLI agent backend."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from .base import AgentBackend, AgentConfig, AgentResult, AgentType


class ClaudeAgent(AgentBackend):
    """Agent backend for Claude Code CLI."""

    agent_type = AgentType.CLAUDE

    # Default allowed tools for sandboxed operation
    DEFAULT_ALLOWED_TOOLS = [
        "Edit",
        "Write",
        "Read",
        "Glob",
        "Grep",
        "Bash(git:*)",
        "Bash(npm:*)",
        "Bash(npx:*)",
        "Bash(python:*)",
        "Bash(pip:*)",
        "Bash(pytest:*)",
        "Bash(make:*)",
        "Bash(cargo:*)",
        "Bash(go:*)",
    ]

    def __init__(self, config: AgentConfig):
        """Initialize the Claude agent backend."""
        super().__init__(config)
        self._cli_path: str | None = None

    def is_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        return self._find_cli() is not None

    def _find_cli(self) -> str | None:
        """Find the Claude CLI executable."""
        if self._cli_path:
            return self._cli_path

        # Check common locations
        cli_name = "claude"
        path = shutil.which(cli_name)
        if path:
            self._cli_path = path
            return path

        # Check npm global bin
        npm_paths = [
            Path.home() / ".npm-global" / "bin" / cli_name,
            Path.home() / "node_modules" / ".bin" / cli_name,
            Path("/usr/local/bin") / cli_name,
        ]
        for p in npm_paths:
            if p.exists():
                self._cli_path = str(p)
                return self._cli_path

        return None

    def get_version(self) -> str | None:
        """Get the Claude CLI version."""
        import subprocess

        cli = self._find_cli()
        if not cli:
            return None

        try:
            result = subprocess.run(
                [cli, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def build_command(self, prompt: str) -> list[str]:
        """Build the Claude CLI command."""
        cli = self._find_cli()
        if not cli:
            raise RuntimeError("Claude CLI not found")

        cmd = [
            cli,
            "-p",  # Print/headless mode
            prompt,
            "--dangerously-skip-permissions",  # YOLO mode
        ]

        # Add allowed tools for sandboxing
        allowed_tools = self.config.allowed_tools or self.DEFAULT_ALLOWED_TOOLS
        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        # Add max tokens if specified
        if self.config.max_tokens:
            cmd.extend(["--max-tokens", str(self.config.max_tokens)])

        # Add any extra arguments
        cmd.extend(self.config.extra_args)

        return cmd

    async def run(self, prompt: str) -> AgentResult:
        """Run Claude with the given prompt."""
        try:
            cmd = self.build_command(prompt)
        except RuntimeError as e:
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=str(e),
            )

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.config.working_dir,
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
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error="Claude CLI executable not found",
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
        """Parse Claude CLI output for metrics and signals."""
        result = super().parse_output(output, exit_code)

        # Claude-specific parsing for cost/token info
        # Claude often outputs stats in a specific format
        import re

        # Look for Claude's cost summary format
        cost_match = re.search(r"Total cost:\s*\$?([\d.]+)", output)
        if cost_match:
            result.cost = float(cost_match.group(1))

        tokens_match = re.search(r"Total tokens:\s*([\d,]+)", output)
        if tokens_match:
            result.tokens_used = int(tokens_match.group(1).replace(",", ""))

        return result

