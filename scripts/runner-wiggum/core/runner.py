"""Main runner orchestration for Ralph Wiggum agent loops."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from agents.base import AgentBackend, AgentConfig, AgentResult, AgentType
from agents.registry import create_agent, list_available_agents
from .prd import PRD, Story
from .progress import ProgressLogger, RunRecord


class RunnerState(Enum):
    """Current state of the runner."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class RunnerConfig:
    """Configuration for the runner."""

    project_path: Path
    agent_type: AgentType = AgentType.CLAUDE
    max_iterations: int = 10
    allow_network: bool = True
    auto_restart: bool = False
    timeout_seconds: int = 600
    prompt_template_path: Path | None = None
    prd_path: Path | None = None


@dataclass
class RunnerStats:
    """Statistics for the current runner session."""

    iterations_completed: int = 0
    stories_completed: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    start_time: datetime | None = None
    end_time: datetime | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


class Runner:
    """Main orchestrator for Ralph Wiggum agent loops."""

    def __init__(self, config: RunnerConfig):
        """Initialize the runner."""
        self.config = config
        self.state = RunnerState.IDLE
        self.stats = RunnerStats()
        self.prd: PRD | None = None
        self.progress: ProgressLogger | None = None
        self.agent: AgentBackend | None = None
        self._current_run: RunRecord | None = None
        self._stop_requested = False

        # Callbacks for TUI updates
        self._on_state_change: Callable[[RunnerState], None] | None = None
        self._on_iteration_start: Callable[[int, Story | None], None] | None = None
        self._on_iteration_end: Callable[[int, AgentResult], None] | None = None
        self._on_output: Callable[[str], None] | None = None

    def set_callbacks(
        self,
        on_state_change: Callable[[RunnerState], None] | None = None,
        on_iteration_start: Callable[[int, Story | None], None] | None = None,
        on_iteration_end: Callable[[int, AgentResult], None] | None = None,
        on_output: Callable[[str], None] | None = None,
    ) -> None:
        """Set callbacks for runner events."""
        self._on_state_change = on_state_change
        self._on_iteration_start = on_iteration_start
        self._on_iteration_end = on_iteration_end
        self._on_output = on_output

    def _set_state(self, state: RunnerState) -> None:
        """Update state and notify callback."""
        self.state = state
        if self._on_state_change:
            self._on_state_change(state)

    def initialize(self) -> bool:
        """Initialize the runner with PRD and agent."""
        try:
            # Load PRD
            prd_path = self.config.prd_path or (self.config.project_path / "prd.json")
            if not prd_path.exists():
                self.stats.errors.append(f"PRD not found: {prd_path}")
                return False

            self.prd = PRD.load(prd_path)

            # Initialize progress logger
            session_id = f"ralph-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            self.progress = ProgressLogger(
                session_id=session_id,
                project_path=self.config.project_path,
            )
            self.progress.initialize()

            # Initialize agent
            agent_config = AgentConfig(
                working_dir=self.config.project_path,
                allow_network=self.config.allow_network,
                timeout_seconds=self.config.timeout_seconds,
            )

            self.agent = create_agent(self.config.agent_type, agent_config)

            if not self.agent.is_available():
                self.stats.errors.append(
                    f"{self.config.agent_type.value} CLI not found"
                )
                return False

            return True

        except Exception as e:
            self.stats.errors.append(f"Initialization error: {e}")
            return False

    def _build_prompt(self, story: Story | None) -> str:
        """Build the prompt for the agent."""
        template = self._load_prompt_template()

        # Build context
        progress_content = ""
        if self.progress:
            progress_content = self.progress.load_existing_progress()

        story_context = ""
        if story:
            story_context = f"""
## Current Story

**ID**: {story.id}
**Title**: {story.title}
**Description**: {story.description}

### Acceptance Criteria
{chr(10).join(f'- {c}' for c in story.acceptance_criteria)}
"""

        prd_status = ""
        if self.prd:
            prd_status = f"""
## PRD Status

Project: {self.prd.project_name}
Progress: {self.prd.completed_stories}/{self.prd.total_stories} stories complete ({self.prd.progress_percent:.0f}%)
"""

        # Substitute into template
        prompt = template.replace("{{STORY}}", story_context)
        prompt = prompt.replace("{{PROGRESS}}", progress_content)
        prompt = prompt.replace("{{PRD_STATUS}}", prd_status)

        return prompt

    def _load_prompt_template(self) -> str:
        """Load the prompt template from project or default location."""
        # First preference: project root prompt.md
        template_path = self.config.prompt_template_path or (
            self.config.project_path / "prompt.md"
        )
        if template_path.exists():
            return template_path.read_text()

        # Fallback: bundled template in runner-wiggum/templates
        bundled_template = Path(__file__).resolve().parents[1] / "templates" / "prompt.md"
        if bundled_template.exists():
            return bundled_template.read_text()

        # Final fallback: minimal safe template
        return "{{PRD_STATUS}}\n\n{{STORY}}\n\n{{PROGRESS}}\n"

    async def run(self) -> None:
        """Run the main agent loop."""
        if not self.initialize():
            self._set_state(RunnerState.ERROR)
            return

        self._set_state(RunnerState.RUNNING)
        self.stats.start_time = datetime.now()
        self._stop_requested = False

        iteration = 0

        while iteration < self.config.max_iterations and not self._stop_requested:
            iteration += 1

            # Check if PRD is complete
            if self.prd and self.prd.is_complete:
                if self._on_output:
                    self._on_output("All stories complete!")
                break

            # Get next story
            story = self.prd.get_next_incomplete_story() if self.prd else None

            # Notify iteration start
            if self._on_iteration_start:
                self._on_iteration_start(iteration, story)

            # Start run record
            if self.progress:
                self._current_run = self.progress.start_run(
                    iteration=iteration,
                    story_id=story.id if story else None,
                )

            # Build and execute prompt
            prompt = self._build_prompt(story)
            if self._on_output:
                self._on_output(f"Starting iteration {iteration}...")

            if self.agent:
                result = await self.agent.run(prompt)
            else:
                result = AgentResult(
                    success=False,
                    output="",
                    exit_code=-1,
                    error="No agent configured",
                )

            # Update stats
            self.stats.iterations_completed = iteration
            if result.tokens_used:
                self.stats.total_tokens += result.tokens_used
            if result.cost:
                self.stats.total_cost += result.cost

            # End run record
            if self.progress and self._current_run:
                self.progress.end_run(
                    self._current_run,
                    success=result.success,
                    summary=result.summary,
                    tokens_used=result.tokens_used,
                    cost=result.cost,
                    error=result.error,
                )
                # Log the run completion to progress.txt
                self.progress.log_run_completion(self._current_run)

                # Extract and log any decisions/learnings from the agent output
                if result.output:
                    self.progress.extract_decisions_from_output(result.output)

            # Notify iteration end
            if self._on_iteration_end:
                self._on_iteration_end(iteration, result)

            # Check for completion signal
            if result.complete_signal and story:
                self.prd.mark_story_complete(story.id)
                self.prd.save()
                self.stats.stories_completed += 1
                if self._on_output:
                    self._on_output(f"Story {story.id} marked complete!")

            # Handle errors
            if result.error:
                self.stats.errors.append(result.error)
                if self._on_output:
                    self._on_output(f"Error: {result.error}")

            # Small delay between iterations
            await asyncio.sleep(1)

        self.stats.end_time = datetime.now()

        # Determine final state
        if self._stop_requested:
            self._set_state(RunnerState.PAUSED)
        elif self.prd and self.prd.is_complete:
            self._set_state(RunnerState.COMPLETED)
        elif iteration >= self.config.max_iterations:
            self._set_state(RunnerState.IDLE)
            if self._on_output:
                self._on_output(f"Reached max iterations ({self.config.max_iterations})")
        else:
            self._set_state(RunnerState.IDLE)

    def stop(self) -> None:
        """Request the runner to stop after current iteration."""
        self._stop_requested = True

    def reset(self) -> None:
        """Reset the runner for a new session."""
        self.state = RunnerState.IDLE
        self.stats = RunnerStats()
        self._current_run = None
        self._stop_requested = False

    def get_available_agents(self) -> list[tuple[AgentType, bool, str | None]]:
        """Get list of agents with availability status."""
        return list_available_agents(self.config.project_path)

