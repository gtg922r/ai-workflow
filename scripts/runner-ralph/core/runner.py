"""Main runner orchestration for Runner Ralph agent loops."""

from __future__ import annotations

import asyncio
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from agents.base import AgentBackend, AgentConfig, AgentResult, AgentType
from agents.registry import create_agent, list_available_agents
from .git import (
    GitManager,
    GitError,
    DirtyWorkingDirectoryError,
    BranchError,
    MergeConflictError,
)
from .prd import PRD, Story, StoryType
from .progress import ProgressLogger, RunRecord
from .worklog import WorkLog, WorkLogEntry, WorkLogManager

# Pattern to extract review verdict from agent output
VERDICT_PATTERN = re.compile(r"<verdict>(APPROVE|REJECT)</verdict>", re.IGNORECASE)


class ReviewVerdict(Enum):
    """Result of a code review."""

    APPROVE = "approve"
    REJECT = "reject"
    UNKNOWN = "unknown"  # Could not extract verdict


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
    git_enabled: bool = True  # Enable git state management
    main_branch: str = "main"  # Name of main/default branch
    use_main_as_base: bool = False  # If True, always branch from main; if False, use current branch
    review_enabled: bool = False  # Enable post-implementation review phase
    model: str | None = None  # Model to use (passed to agent CLI --model flag)


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
    """Main orchestrator for Runner Ralph agent loops."""

    def __init__(self, config: RunnerConfig):
        """Initialize the runner."""
        self.config = config
        self.state = RunnerState.IDLE
        self.stats = RunnerStats()
        self.prd: PRD | None = None
        self.progress: ProgressLogger | None = None
        self.agent: AgentBackend | None = None
        self.git: GitManager | None = None
        self.worklog_manager: WorkLogManager | None = None
        self._current_run: RunRecord | None = None
        self._current_story: Story | None = None
        self._current_worklog: WorkLog | None = None
        self._stop_requested = False

        # Callbacks for TUI updates
        self._on_state_change: Callable[[RunnerState], None] | None = None
        self._on_iteration_start: Callable[[int, Story | None], None] | None = None
        self._on_iteration_end: Callable[[int, AgentResult], None] | None = None
        self._on_output: Callable[[str], None] | None = None
        self._on_git_dirty: Callable[[str], bool] | None = None  # Return True to disable git and continue
        self._on_git_reset_prompt: Callable[[str], bool] | None = None  # Return True to reset
        self._on_worklog_entry: Callable[[str, WorkLogEntry], None] | None = None  # (story_id, entry)

    def set_callbacks(
        self,
        on_state_change: Callable[[RunnerState], None] | None = None,
        on_iteration_start: Callable[[int, Story | None], None] | None = None,
        on_iteration_end: Callable[[int, AgentResult], None] | None = None,
        on_output: Callable[[str], None] | None = None,
        on_git_dirty: Callable[[str], bool] | None = None,
        on_git_reset_prompt: Callable[[str], bool] | None = None,
        on_worklog_entry: Callable[[str, WorkLogEntry], None] | None = None,
    ) -> None:
        """Set callbacks for runner events.

        Args:
            on_state_change: Called when runner state changes
            on_iteration_start: Called at the start of each iteration
            on_iteration_end: Called at the end of each iteration
            on_output: Called for general output messages
            on_git_dirty: Called when working directory is dirty. Return True to disable git and continue.
            on_git_reset_prompt: Called on failure to prompt for branch reset. Return True to reset.
            on_worklog_entry: Called when a worklog entry is added. Args: (story_id, entry)
        """
        self._on_state_change = on_state_change
        self._on_iteration_start = on_iteration_start
        self._on_iteration_end = on_iteration_end
        self._on_output = on_output
        self._on_git_dirty = on_git_dirty
        self._on_git_reset_prompt = on_git_reset_prompt
        self._on_worklog_entry = on_worklog_entry

    def _set_state(self, state: RunnerState) -> None:
        """Update state and notify callback."""
        self.state = state
        if self._on_state_change:
            self._on_state_change(state)

    def initialize(self) -> bool:
        """Initialize the runner with PRD, agent, and git manager."""
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

            # Initialize worklog manager
            self.worklog_manager = WorkLogManager(
                project_path=self.config.project_path,
                on_entry=self._on_worklog_entry,
            )

            # Initialize git manager if enabled
            if self.config.git_enabled:
                self.git = GitManager(
                    repo_path=self.config.project_path,
                    main_branch=self.config.main_branch,
                    on_output=self._on_output,
                    use_current_branch_as_base=not self.config.use_main_as_base,
                )

                # Check if it's a git repo
                if not self.git.is_git_repo():
                    if self._on_output:
                        self._on_output("Warning: Not a git repository, disabling git management")
                    self.git = None
                else:
                    # Check for clean working directory
                    if not self._check_git_clean_state():
                        return False

                    # Initialize git manager to capture the base branch
                    self.git.initialize()

            # Initialize agent
            agent_config = AgentConfig(
                working_dir=self.config.project_path,
                allow_network=self.config.allow_network,
                timeout_seconds=self.config.timeout_seconds,
                model=self.config.model,
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

    def _check_git_clean_state(self) -> bool:
        """Check if git working directory is clean.

        When dirty state is detected:
        - If callback returns True: disable git management and continue
        - If callback returns False: abort the run

        Returns:
            True if clean or user chose to disable git, False to abort
        """
        if not self.git:
            return True

        try:
            self.git.check_clean_state()
            return True
        except DirtyWorkingDirectoryError as e:
            # Callback to ask user what to do
            if self._on_git_dirty:
                if self._on_git_dirty(e.status):
                    # User chose to disable git and continue
                    if self._on_output:
                        self._on_output("Disabling git management for this session...")
                    self.git = None
                    return True
                else:
                    self.stats.errors.append("Aborted: working directory not clean")
                    return False
            else:
                # No callback, fail by default
                self.stats.errors.append(f"Working directory not clean:\n{e.status}")
                return False

    def _setup_story_branch(self, story: Story) -> bool:
        """Create or switch to the story branch.

        Returns:
            True if successful, False otherwise
        """
        if not self.git:
            return True

        try:
            branch_name = self.git.create_story_branch(story.id)
            if self._on_output:
                self._on_output(f"Working on branch: {branch_name}")
            return True
        except BranchError as e:
            self.stats.errors.append(f"Git branch error: {e}")
            return False

    def _commit_and_merge_story(self, story: Story) -> bool:
        """Commit story changes and merge back to main.

        Returns:
            True if successful, False otherwise
        """
        if not self.git:
            return True

        try:
            # Commit all changes
            commit_hash = self.git.commit_story_completion(story.id, story.title)
            if commit_hash:
                if self._on_output:
                    self._on_output(f"Committed changes: {commit_hash[:8]}")

            # Merge to base branch
            self.git.merge_to_main(delete_branch=True)
            if self._on_output:
                self._on_output(f"Merged {story.id} to {self.git.base_branch}")

            return True

        except MergeConflictError as e:
            self.stats.errors.append(f"Merge conflict: {e}")
            if self._on_output:
                self._on_output(f"Merge conflict occurred: {e}")
            return False

        except GitError as e:
            self.stats.errors.append(f"Git error during commit/merge: {e}")
            return False

    def _commit_session_cleanup(self) -> bool:
        """Commit any remaining session files and return to main branch.

        Called at the end of the run to ensure git finishes clean and on main.

        Returns:
            True if successful, False on error
        """
        if not self.git:
            return True

        try:
            status = self.git.get_status()

            # Commit any uncommitted changes first
            if not status.is_clean:
                if self.git.stage_all_changes():
                    commit_hash = self.git.commit("chore: update session files (progress, prd, worklogs)")
                    if commit_hash:
                        if self._on_output:
                            self._on_output(f"Committed session cleanup: {commit_hash[:8]}")

            # Return to main branch if on a story branch
            status = self.git.get_status()  # Refresh status after commit
            if status.is_story_branch:
                self.git.return_to_main()
                if self._on_output:
                    self._on_output(f"Returned to {self.git.base_branch}")

            return True

        except GitError as e:
            if self._on_output:
                self._on_output(f"Warning: Failed to complete session cleanup: {e}")
            return False

    def _handle_story_failure(self, story: Story) -> None:
        """Handle story failure - offer to reset branch.

        Args:
            story: The failed story
        """
        if not self.git:
            return

        status = self.git.get_status()
        if not status.is_story_branch:
            return

        # Check if there are uncommitted changes
        if status.is_clean:
            return

        changes_summary = self.git.get_uncommitted_changes_summary()
        prompt_msg = (
            f"Story {story.id} failed with uncommitted changes:\n"
            f"{changes_summary}\n\n"
            "Reset branch and discard changes?"
        )

        if self._on_git_reset_prompt:
            if self._on_git_reset_prompt(prompt_msg):
                try:
                    self.git.abort_and_return_to_main(story.id)
                    if self._on_output:
                        self._on_output(f"Reset branch and returned to {self.git.base_branch}")
                except GitError as e:
                    if self._on_output:
                        self._on_output(f"Failed to reset branch: {e}")

    def _build_prompt(self, story: Story | None) -> str:
        """Build the prompt for the agent."""
        story_type = story.story_type if story else None
        template = self._load_prompt_template(story_type)

        # Build context
        progress_content = ""
        if self.progress:
            progress_content = self.progress.load_existing_progress()

        story_context = ""
        if story:
            feature_spec = ""
            if story.feature_spec:
                feature_spec = f"""
### Feature Spec
{chr(10).join(f'- {s}' for s in story.feature_spec)}
"""
            story_context = f"""
## Current Story

**ID**: {story.id}
**Title**: {story.title}
**Description**: {story.description}
{feature_spec}

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

    def _load_prompt_template(self, story_type: StoryType | None = None) -> str:
        """Load the prompt template from project or default location.

        Template resolution order:
        1. Type-specific template in project root: prompt_{type}.md
        2. Generic template in project root: prompt.md
        3. Type-specific bundled template: templates/prompt_{type}.md
        4. Generic bundled template: templates/prompt.md
        5. Minimal fallback template

        Args:
            story_type: Optional story type to look for type-specific templates
        """
        templates_dir = Path(__file__).resolve().parents[1] / "templates"

        # Type-specific template filename
        type_template_name = f"prompt_{story_type.value}.md" if story_type else None

        # 1. Type-specific in project root (if type specified)
        if type_template_name:
            project_type_template = self.config.project_path / type_template_name
            if project_type_template.exists():
                return project_type_template.read_text()

        # 2. Generic in project root (or custom path)
        generic_path = self.config.prompt_template_path or (
            self.config.project_path / "prompt.md"
        )
        if generic_path.exists():
            return generic_path.read_text()

        # 3. Type-specific bundled template (if type specified)
        if type_template_name:
            bundled_type_template = templates_dir / type_template_name
            if bundled_type_template.exists():
                return bundled_type_template.read_text()

        # 4. Generic bundled template
        bundled_template = templates_dir / "prompt.md"
        if bundled_template.exists():
            return bundled_template.read_text()

        # 5. Final fallback: minimal safe template
        return "{{PRD_STATUS}}\n\n{{STORY}}\n\n{{PROGRESS}}\n"

    def _load_review_template(self) -> str:
        """Load the review prompt template."""
        # Bundled template in runner-ralph/templates
        bundled_template = Path(__file__).resolve().parents[1] / "templates" / "review.md"
        if bundled_template.exists():
            return bundled_template.read_text()

        # Fallback: minimal review template
        return """# Code Review
Review the changes for story {{STORY_ID}}.

## Changes
```diff
{{DIFF}}
```

End with: `<verdict>APPROVE</verdict>` or `<verdict>REJECT</verdict>`
"""

    def _build_review_prompt(self, story: Story) -> str:
        """Build the review prompt for a completed story.

        Args:
            story: The story that was just completed

        Returns:
            The review prompt with context filled in
        """
        template = self._load_review_template()

        # Get git diff if available
        diff = ""
        diff_stats = ""
        if self.git:
            diff = self.git.get_diff_from_main()
            diff_stats = self.git.get_diff_stat_from_main()

        # Load AGENTS.md from project root
        agents_md_path = self.config.project_path / "AGENTS.md"
        agents_md = ""
        if agents_md_path.exists():
            agents_md = agents_md_path.read_text()
        else:
            agents_md = "(No AGENTS.md found in project root)"

        # Format acceptance criteria
        acceptance_criteria = "\n".join(f"- {c}" for c in story.acceptance_criteria)

        # Substitute into template
        prompt = template.replace("{{STORY_ID}}", story.id)
        prompt = prompt.replace("{{STORY_TITLE}}", story.title)
        prompt = prompt.replace("{{STORY_DESCRIPTION}}", story.description)
        prompt = prompt.replace("{{ACCEPTANCE_CRITERIA}}", acceptance_criteria)
        prompt = prompt.replace("{{AGENTS_MD}}", agents_md)
        prompt = prompt.replace("{{DIFF_STATS}}", diff_stats)
        prompt = prompt.replace("{{DIFF}}", diff)

        return prompt

    def _extract_verdict(self, output: str) -> tuple[ReviewVerdict, str]:
        """Extract the review verdict from agent output.

        Args:
            output: The agent's review output

        Returns:
            Tuple of (verdict, full_review_text)
        """
        match = VERDICT_PATTERN.search(output)
        if match:
            verdict_str = match.group(1).upper()
            if verdict_str == "APPROVE":
                return ReviewVerdict.APPROVE, output
            elif verdict_str == "REJECT":
                return ReviewVerdict.REJECT, output

        return ReviewVerdict.UNKNOWN, output

    async def _run_review_phase(self, story: Story) -> tuple[ReviewVerdict, str]:
        """Run the review phase for a completed story.

        Args:
            story: The story to review

        Returns:
            Tuple of (verdict, review_output)
        """
        if self._on_output:
            self._on_output(f"Starting review phase for {story.id}...")

        prompt = self._build_review_prompt(story)

        if self.agent:
            result = await self.agent.run(prompt)
            verdict, review_text = self._extract_verdict(result.output)

            # Update stats
            if result.tokens_used:
                self.stats.total_tokens += result.tokens_used
            if result.cost:
                self.stats.total_cost += result.cost

            return verdict, review_text
        else:
            return ReviewVerdict.UNKNOWN, "No agent configured for review"

    async def run(self) -> None:
        """Run the main agent loop."""
        if not self.initialize():
            self._set_state(RunnerState.ERROR)
            return

        self._set_state(RunnerState.RUNNING)
        self.stats.start_time = datetime.now()
        self._stop_requested = False

        iteration = 0
        last_story_id: str | None = None

        while iteration < self.config.max_iterations and not self._stop_requested:
            iteration += 1

            # Check if PRD is complete
            if self.prd and self.prd.is_complete:
                if self._on_output:
                    self._on_output("All stories complete!")
                break

            # Get next story
            story = self.prd.get_next_incomplete_story() if self.prd else None
            self._current_story = story

            # Setup git branch and worklog for new story (only when story changes)
            if story and story.id != last_story_id:
                if not self._setup_story_branch(story):
                    self._set_state(RunnerState.ERROR)
                    return
                last_story_id = story.id

                # Create/get worklog for this story
                if self.worklog_manager:
                    self._current_worklog = self.worklog_manager.get_or_create(
                        story.id, story.title
                    )
                    self._current_worklog.log_progress(f"Starting work on story: {story.title}")

            # Notify iteration start
            if self._on_iteration_start:
                self._on_iteration_start(iteration, story)

            # Log iteration start to worklog
            if self._current_worklog:
                self._current_worklog.log_progress(f"Beginning iteration {iteration}")

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

            # Extract decisions/learnings to worklog
            if self._current_worklog and result.output:
                self._current_worklog.extract_from_output(result.output)
                self._current_worklog.log_progress(
                    f"Iteration {iteration} completed: {result.summary[:100]}"
                )

            # Notify iteration end
            if self._on_iteration_end:
                self._on_iteration_end(iteration, result)

            # Check for completion signal
            if result.complete_signal and story:
                # Run review phase if enabled
                review_passed = True
                if self.config.review_enabled:
                    verdict, review_output = await self._run_review_phase(story)

                    # Log review output to progress.txt
                    if self.progress:
                        self.progress.log_review(story.id, verdict.value, review_output)

                    if verdict == ReviewVerdict.APPROVE:
                        if self._on_output:
                            self._on_output(f"Review APPROVED for {story.id}")
                        review_passed = True
                    elif verdict == ReviewVerdict.REJECT:
                        if self._on_output:
                            self._on_output(f"Review REJECTED for {story.id} - reopening story")
                        review_passed = False

                        # Log rejection to worklog
                        if self._current_worklog:
                            self._current_worklog.log_error(
                                f"Review rejected - story reopened for revision"
                            )

                        # Reopen the story with feedback
                        self.prd.reopen_story(story.id, review_output)
                        self.prd.save()

                        # Don't merge, continue to next iteration
                        continue
                    else:
                        # Unknown verdict - treat as warning, proceed with completion
                        if self._on_output:
                            self._on_output(f"Warning: Could not determine review verdict for {story.id}")

                # Git: commit and merge on story completion (only if review passed)
                if review_passed and self.git:
                    if not self._commit_and_merge_story(story):
                        # Merge failed, but story is complete - log warning
                        if self._on_output:
                            self._on_output("Warning: Story completed but git merge failed")

                self.prd.mark_story_complete(story.id)
                self.prd.save()
                self.stats.stories_completed += 1
                if self._on_output:
                    self._on_output(f"Story {story.id} marked complete!")

                # Get worklog summary before finalizing
                worklog_summary = None
                if self._current_worklog:
                    worklog_summary = self._current_worklog.get_summary()

                # Log story completion to progress.txt with worklog summary
                if self.progress:
                    self.progress.log_story_completion(
                        story.id,
                        story.title,
                        worklog_summary=worklog_summary,
                    )

                # Finalize worklog for completed story
                if self.worklog_manager:
                    self.worklog_manager.finalize_story(
                        story.id,
                        success=True,
                        summary=f"Story completed successfully after {iteration} iteration(s)",
                    )
                self._current_worklog = None

                # Reset last_story_id so next story gets its own branch
                last_story_id = None

            # Handle errors - offer to reset on failure
            if result.error:
                self.stats.errors.append(result.error)
                if self._on_output:
                    self._on_output(f"Error: {result.error}")

                # Log error to worklog
                if self._current_worklog:
                    self._current_worklog.log_error(result.error)

                # Offer to reset branch on failure
                if story and not result.complete_signal:
                    self._handle_story_failure(story)

            # Small delay between iterations
            await asyncio.sleep(1)

        self.stats.end_time = datetime.now()

        # Commit any remaining session files to leave git clean
        self._commit_session_cleanup()

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

    def reset(self, reset_git_branch: bool = False) -> None:
        """Reset the runner for a new session.

        Args:
            reset_git_branch: If True, also reset git branch and return to main
        """
        if reset_git_branch and self.git and self._current_story:
            try:
                self.git.abort_and_return_to_main(self._current_story.id)
                if self._on_output:
                    self._on_output(f"Reset git branch for {self._current_story.id}")
            except GitError as e:
                if self._on_output:
                    self._on_output(f"Warning: Failed to reset git branch: {e}")

        self.state = RunnerState.IDLE
        self.stats = RunnerStats()
        self._current_run = None
        self._current_story = None
        self._stop_requested = False

    def reset_git_branch(self, story_id: str | None = None) -> bool:
        """Reset the git branch for a story and return to main.

        Args:
            story_id: The story ID to reset. Uses current story if None.

        Returns:
            True if reset was successful
        """
        if not self.git:
            return False

        target_id = story_id or (self._current_story.id if self._current_story else None)
        if not target_id:
            if self._on_output:
                self._on_output("No story to reset")
            return False

        try:
            self.git.abort_and_return_to_main(target_id)
            if self._on_output:
                self._on_output(f"Reset branch and returned to {self.git.base_branch}")
            return True
        except GitError as e:
            if self._on_output:
                self._on_output(f"Failed to reset branch: {e}")
            return False

    def get_git_status_summary(self) -> str | None:
        """Get a summary of current git status.

        Returns:
            Human-readable git status or None if git not enabled
        """
        if not self.git:
            return None

        try:
            status = self.git.get_status()
            parts = [f"Branch: {status.current_branch}"]

            if status.is_story_branch:
                parts.append(f"Story: {status.story_id}")

            if not status.is_clean:
                changes = []
                if status.has_staged:
                    changes.append("staged")
                if status.has_unstaged:
                    changes.append("unstaged")
                if status.has_untracked:
                    changes.append("untracked")
                parts.append(f"Changes: {', '.join(changes)}")
            else:
                parts.append("Clean")

            return " | ".join(parts)
        except GitError:
            return "Git status unavailable"

    def get_available_agents(self) -> list[tuple[AgentType, bool, str | None]]:
        """Get list of agents with availability status."""
        return list_available_agents(self.config.project_path)

