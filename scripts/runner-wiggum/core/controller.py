"""Controller layer that mediates between the TUI and the runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from agents.base import AgentResult, AgentType
from agents.registry import list_available_agents
from .prd import Story
from .runner import Runner, RunnerConfig, RunnerState


@dataclass
class RunnerCallbacks:
    """Collection of callbacks for runner events."""

    on_state_change: Callable[[RunnerState], None] | None = None
    on_iteration_start: Callable[[int, Story | None], None] | None = None
    on_iteration_end: Callable[[int, AgentResult], None] | None = None
    on_output: Callable[[str], None] | None = None
    on_git_dirty: Callable[[str], bool] | None = None
    on_git_reset_prompt: Callable[[str], bool] | None = None


class RunnerController:
    """Coordinates runner lifecycle without UI concerns."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.config: RunnerConfig | None = None
        self.runner: Runner | None = None
        self.callbacks = RunnerCallbacks()

    def set_callbacks(self, callbacks: RunnerCallbacks) -> None:
        """Set callbacks for runner events."""
        self.callbacks = callbacks

    def get_available_agents(self) -> list[tuple[AgentType, bool, str | None]]:
        """List available agent backends and their versions."""
        return list_available_agents(self.project_path)

    def configure(self, config: RunnerConfig) -> None:
        """Configure a new runner instance."""
        self.config = config
        self.runner = Runner(config)
        if self.callbacks and self.runner:
            self.runner.set_callbacks(
                on_state_change=self.callbacks.on_state_change,
                on_iteration_start=self.callbacks.on_iteration_start,
                on_iteration_end=self.callbacks.on_iteration_end,
                on_output=self.callbacks.on_output,
                on_git_dirty=self.callbacks.on_git_dirty,
                on_git_reset_prompt=self.callbacks.on_git_reset_prompt,
            )

    async def run(self) -> None:
        """Run the configured runner."""
        if not self.runner:
            raise RuntimeError("Runner not configured")
        await self.runner.run()

    def stop(self) -> None:
        """Request the runner to stop after current iteration."""
        if self.runner:
            self.runner.stop()

    def reset(self, reset_git_branch: bool = False) -> None:
        """Reset the runner for a new session.

        Args:
            reset_git_branch: If True, also reset git branch and return to main
        """
        if self.runner:
            self.runner.reset(reset_git_branch=reset_git_branch)

    def reset_git_branch(self, story_id: str | None = None) -> bool:
        """Reset the git branch for a story and return to main.

        Args:
            story_id: The story ID to reset. Uses current story if None.

        Returns:
            True if reset was successful
        """
        if self.runner:
            return self.runner.reset_git_branch(story_id)
        return False

    def get_git_status(self) -> str | None:
        """Get current git status summary.

        Returns:
            Human-readable git status or None if git not enabled
        """
        if self.runner:
            return self.runner.get_git_status_summary()
        return None
