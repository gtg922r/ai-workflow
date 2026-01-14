"""Cursor CLI agent backend.

Updated for Cursor CLI Jan 2026 release.
See: https://cursor.com/changelog/cli-jan-08-2026
     https://cursor.com/docs/cli/using
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from .base import AgentBackend, AgentConfig, AgentResult, AgentType


class CursorAgent(AgentBackend):
    """Agent backend for Cursor CLI.

    The Cursor CLI uses the `agent` command for headless operation.
    In non-interactive mode (-p/--print), it has full write access automatically.
    """

    agent_type = AgentType.CURSOR

    def __init__(self, config: AgentConfig):
        """Initialize the Cursor agent backend."""
        super().__init__(config)
        self._cli_path: str | None = None

    def is_available(self) -> bool:
        """Check if Cursor CLI is available."""
        return self._find_cli() is not None

    def _find_cli(self) -> str | None:
        """Find the Cursor CLI executable."""
        if self._cli_path:
            return self._cli_path

        # The Cursor CLI command is `agent` as of Jan 2026
        for cli_name in ["agent", "cursor"]:
            path = shutil.which(cli_name)
            if path:
                self._cli_path = path
                return path

        # Check common installation locations
        common_paths = [
            Path.home() / ".local" / "bin" / "agent",
            Path.home() / ".cursor" / "bin" / "agent",
            Path("/usr/local/bin/agent"),
        ]
        for p in common_paths:
            if p.exists():
                self._cli_path = str(p)
                return self._cli_path

        return None

    def get_version(self) -> str | None:
        """Get the Cursor CLI version."""
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
        """Build the Cursor CLI command.

        Uses non-interactive mode (-p) which has full write access automatically.
        Output format is set to JSON for easier parsing.
        """
        cli = self._find_cli()
        if not cli:
            raise RuntimeError("Cursor CLI not found")

        cmd = [
            cli,
            "-p",  # Print/non-interactive mode (full write access)
            "--output-format", "text",  # Use text for readable output (json available)
            prompt,
        ]

        # Add any extra arguments
        cmd.extend(self.config.extra_args)

        return cmd

    async def run(self, prompt: str) -> AgentResult:
        """Run Cursor with the given prompt."""
        try:
            cmd = self.build_command(prompt)
        except RuntimeError as e:
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=str(e),
            )

        # Set up environment with API key if available
        import os

        env = os.environ.copy()
        # CURSOR_API_KEY should already be set in environment

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
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error="Cursor CLI executable not found",
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
        """Parse Cursor CLI output for metrics and signals."""
        result = super().parse_output(output, exit_code)

        # Cursor-specific parsing
        import re

        # Look for Cursor's stats format (if available)
        tokens_match = re.search(r"tokens?\s*used:\s*([\d,]+)", output, re.IGNORECASE)
        if tokens_match:
            result.tokens_used = int(tokens_match.group(1).replace(",", ""))

        # Parse JSON output if --output-format json was used
        if output.strip().startswith("{"):
            try:
                import json
                data = json.loads(output)
                if "tokens" in data:
                    result.tokens_used = data["tokens"]
                if "cost" in data:
                    result.cost = data["cost"]
            except json.JSONDecodeError:
                pass

        return result

