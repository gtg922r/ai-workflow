"""Cursor CLI agent backend.

Updated for Cursor CLI Jan 2026 release.
See: https://cursor.com/cli
     https://cursor.com/changelog/cli-jan-08-2026

Install the CLI with:
    curl https://cursor.com/install -fsS | bash
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import AgentBackend, AgentConfig, AgentResult, AgentType


class CursorAgent(AgentBackend):
    """Agent backend for Cursor CLI.

    The Cursor CLI uses the `agent` command for headless operation.
    In non-interactive mode (-p/--print), it runs autonomously with full tool access.

    Install with: curl https://cursor.com/install -fsS | bash
    """

    agent_type = AgentType.CURSOR

    def __init__(self, config: AgentConfig):
        """Initialize the Cursor agent backend."""
        super().__init__(config)
        self._cli_path: str | None = None

    def is_available(self) -> bool:
        """Check if Cursor CLI (agent command) is available."""
        return self._find_cli() is not None

    def _find_cli(self) -> str | None:
        """Find the Cursor CLI executable (agent command)."""
        if self._cli_path:
            return self._cli_path

        # The Cursor CLI command is `agent` (not `cursor` which is just the IDE launcher)
        path = shutil.which("agent")
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

        Uses the `agent` command with:
        - `-p` for print/non-interactive mode (runs autonomously)
        - `--force` to skip confirmations
        - `--output-format text` for readable output
        - `--model` for model selection (if specified)
        """
        cli = self._find_cli()
        if not cli:
            raise RuntimeError(
                "Cursor CLI (agent) not found. "
                "Install with: curl https://cursor.com/install -fsS | bash"
            )

        cmd = [
            cli,
            "-p",  # Print/non-interactive mode
            "--force",  # Skip confirmations for headless operation
            "--output-format", "text",  # Readable output (json also available)
        ]

        # Add model selection if specified
        if self.config.model:
            cmd.extend(["--model", self.config.model])

        # Add prompt as positional argument
        cmd.append(prompt)

        # Add any extra arguments
        cmd.extend(self.config.extra_args)

        return cmd

    async def run(self, prompt: str) -> AgentResult:
        """Run Cursor agent with the given prompt."""
        try:
            cmd = self.build_command(prompt)
        except RuntimeError as e:
            return AgentResult(
                success=False,
                output="",
                exit_code=-1,
                error=str(e),
            )

        # Set up environment
        import os

        env = os.environ.copy()

        # Run the command
        output, exit_code, error = await self._run_subprocess(
            cmd,
            cli_label="Cursor CLI (agent)",
            env=env,
        )
        if error:
            return AgentResult(
                success=False,
                output=output,
                exit_code=exit_code,
                error=error,
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

